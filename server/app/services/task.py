"""Task and reminder business logic."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import logger
from app.core.utils import as_utc, paginate_params
from app.db.models.audit_event import AuditActorType, AuditSource
from app.db.models.google_sync_queue import GoogleSyncQueue, SyncAction, SyncStatus
from app.db.models.reminder import Reminder
from app.db.models.task import Task, TaskStatus
from app.db.models.task_status_history import TaskStatusHistory
from app.schemas.task import (
    ReminderResponse,
    StatusHistoryResponse,
    SyncQueueResponse,
    TaskDetailResponse,
    TaskResponse,
    TaskStatsResponse,
    TaskTextFields,
)
from app.services.audit import AuditService, domain_event
from app.services.search_indexers.task import index_task, remove_task


class TaskService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def require_task(self, *, task_id: int) -> Task:
        task = await self.get_task(task_id=task_id)
        if not task:
            raise NotFoundError("Task not found")
        return task

    async def create_task(
        self,
        *,
        telegram_user_id: int,
        title: str,
        scheduled_at: datetime,
        description: str | None = None,
        location: str | None = None,
        intake_id: int | None = None,
        source: AuditSource = AuditSource.TODOBOT,
        actor_type: AuditActorType = AuditActorType.TELEGRAM,
        actor_id: int | None = None,
    ) -> Task:
        try:
            fields = TaskTextFields(
                title=title,
                description=description,
                location=location,
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        task = Task(
            telegram_user_id=telegram_user_id,
            title=fields.title,
            description=fields.description,
            location=fields.location,
            scheduled_at=as_utc(scheduled_at),
            status=TaskStatus.PENDING,
            intake_id=intake_id,
        )
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        await index_task(self.db, task)
        logger.info("Task created", context={"task_id": task.id, "title": fields.title})

        await AuditService(self.db).record(
            domain_event(
                action="task.created",
                actor_type=actor_type,
                actor_id=actor_id if actor_id is not None else telegram_user_id,
                source=source,
                resource_type="task",
                resource_id=task.id,
                metadata={"title": fields.title},
            ),
        )
        return task

    async def create_reminder(
        self,
        *,
        task_id: int,
        remind_at: datetime,
        job_id: str | None = None,
    ) -> Reminder:
        reminder = Reminder(
            task_id=task_id,
            remind_at=remind_at,
            sent=False,
            job_id=job_id,
        )
        self.db.add(reminder)
        await self.db.flush()
        await self.db.refresh(reminder)
        return reminder

    async def update_task_status(
        self,
        *,
        task: Task,
        new_status: TaskStatus,
        actor_type: AuditActorType = AuditActorType.SYSTEM,
        actor_id: int | None = None,
        source: AuditSource = AuditSource.WORKER,
    ) -> Task:
        """Update status, record history, and emit audit event."""
        old_status = task.status
        task.status = new_status
        self.db.add(task)

        history = TaskStatusHistory(
            task_id=task.id,
            old_status=old_status.value,
            new_status=new_status.value,
        )
        self.db.add(history)
        await self.db.flush()
        await self.db.refresh(task)
        await index_task(self.db, task)

        logger.debug(
            "Task status updated",
            context={
                "task_id": task.id,
                "old": old_status.value,
                "new": new_status.value,
            },
        )

        await AuditService(self.db).record(
            domain_event(
                action="task.status_changed",
                actor_type=actor_type,
                actor_id=actor_id,
                source=source,
                resource_type="task",
                resource_id=task.id,
                metadata={
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                },
            ),
        )
        return task

    async def change_status(
        self,
        *,
        task_id: int,
        new_status: TaskStatus,
        actor_type: AuditActorType = AuditActorType.SYSTEM,
        actor_id: int | None = None,
        source: AuditSource = AuditSource.WORKER,
    ) -> Task:
        task = await self.require_task(task_id=task_id)
        return await self.update_task_status(
            task=task,
            new_status=new_status,
            actor_type=actor_type,
            actor_id=actor_id,
            source=source,
        )

    async def reschedule_task(
        self,
        *,
        task_id: int,
        scheduled_at: datetime,
        actor_type: AuditActorType = AuditActorType.SYSTEM,
        actor_id: int | None = None,
        source: AuditSource = AuditSource.WORKER,
    ) -> Task:
        task = await self.require_task(task_id=task_id)
        task.scheduled_at = as_utc(scheduled_at)
        if task.status == TaskStatus.POSTPONED:
            task.status = TaskStatus.PENDING
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        await index_task(self.db, task)

        await AuditService(self.db).record(
            domain_event(
                action="task.rescheduled",
                actor_type=actor_type,
                actor_id=actor_id,
                source=source,
                resource_type="task",
                resource_id=task.id,
                metadata={"scheduled_at": task.scheduled_at.isoformat()},
            ),
        )

        if task.google_event_id:
            await self.enqueue_calendar_sync(
                task_id=task.id,
                action=SyncAction.UPDATE,
                google_event_id=task.google_event_id,
            )
        return task

    async def schedule_reminder_minutes_before(
        self,
        *,
        task_id: int,
        scheduled_at: datetime,
        minutes_before: int,
    ) -> Reminder | None:
        from app.workers.scheduling import schedule_reminder

        remind_at = as_utc(scheduled_at) - timedelta(minutes=minutes_before)
        if remind_at <= datetime.now(UTC):
            return None

        reminder = await self.create_reminder(task_id=task_id, remind_at=remind_at)
        await schedule_reminder(self.db, reminder)
        return reminder

    async def create_with_sync(
        self,
        *,
        telegram_user_id: int,
        title: str,
        scheduled_at: datetime,
        description: str | None = None,
        location: str | None = None,
        reminder_minutes: int | None = None,
        intake_id: int | None = None,
        source: AuditSource = AuditSource.TODOBOT,
        actor_type: AuditActorType = AuditActorType.TELEGRAM,
        actor_id: int | None = None,
    ) -> Task:
        task = await self.create_task(
            telegram_user_id=telegram_user_id,
            title=title,
            scheduled_at=scheduled_at,
            description=description,
            location=location,
            intake_id=intake_id,
            source=source,
            actor_type=actor_type,
            actor_id=actor_id,
        )
        if reminder_minutes:
            await self.schedule_reminder_minutes_before(
                task_id=task.id,
                scheduled_at=scheduled_at,
                minutes_before=reminder_minutes,
            )
        await self.enqueue_calendar_sync(task_id=task.id, action=SyncAction.CREATE)
        return task

    async def get_task(self, *, task_id: int) -> Task | None:
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def list_tasks(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        status: str | None = None,
    ) -> list[TaskResponse]:
        offset, limit = paginate_params(page, per_page)
        query = select(Task).order_by(Task.created_at.desc())
        if status:
            try:
                TaskStatus(status)
            except ValueError as exc:
                raise ValidationError(f"Invalid task status: {status}") from exc
            query = query.where(Task.status == status)
        result = await self.db.execute(query.offset(offset).limit(limit))
        return [TaskResponse.model_validate(t) for t in result.scalars().all()]

    async def task_stats(self) -> TaskStatsResponse:
        total = await self._count(Task)
        pending = await self._count(Task, Task.status == TaskStatus.PENDING)
        completed = await self._count(Task, Task.status == TaskStatus.COMPLETED)
        failed_syncs = await self._count(
            GoogleSyncQueue,
            GoogleSyncQueue.status == SyncStatus.FAILED,
        )
        return TaskStatsResponse(
            pending=pending,
            completed=completed,
            total=total,
            failed_syncs=failed_syncs,
        )

    async def list_sync_queue(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> list[SyncQueueResponse]:
        offset, limit = paginate_params(page, per_page)
        result = await self.db.execute(
            select(GoogleSyncQueue)
            .order_by(GoogleSyncQueue.created_at.desc())
            .offset(offset)
            .limit(limit),
        )
        return [SyncQueueResponse.model_validate(q) for q in result.scalars().all()]

    async def task_detail(self, task_id: int) -> TaskDetailResponse:
        task = await self.get_task(task_id=task_id)
        if not task:
            raise NotFoundError("Task not found")

        reminders_result = await self.db.execute(
            select(Reminder)
            .where(Reminder.task_id == task_id)
            .order_by(Reminder.remind_at),
        )
        history_result = await self.db.execute(
            select(TaskStatusHistory)
            .where(TaskStatusHistory.task_id == task_id)
            .order_by(TaskStatusHistory.changed_at),
        )

        return TaskDetailResponse(
            **TaskResponse.model_validate(task).model_dump(),
            reminders=[
                ReminderResponse.model_validate(r)
                for r in reminders_result.scalars().all()
            ],
            status_history=[
                StatusHistoryResponse.model_validate(h)
                for h in history_result.scalars().all()
            ],
        )

    async def retry_sync(self, task_id: int) -> int:
        result = await self.db.execute(
            select(GoogleSyncQueue).where(
                GoogleSyncQueue.task_id == task_id,
                GoogleSyncQueue.status == SyncStatus.FAILED,
            ),
        )
        items = list(result.scalars().all())
        if not items:
            raise NotFoundError("No failed sync entries for this task")

        for item in items:
            item.status = SyncStatus.PENDING
            item.attempts = 0
            item.next_retry_at = datetime.now(UTC) + timedelta(seconds=5)
            self.db.add(item)

        await self.db.flush()
        return len(items)

    async def get_pending_tasks(
        self,
        *,
        telegram_user_id: int,
        limit: int = 20,
    ) -> list[Task]:
        result = await self.db.execute(
            select(Task)
            .where(
                Task.telegram_user_id == telegram_user_id,
                Task.status == TaskStatus.PENDING,
            )
            .order_by(Task.scheduled_at)
            .limit(limit),
        )
        return list(result.scalars().all())

    async def get_unsent_reminders(self) -> list[Reminder]:
        now = datetime.now(UTC)
        result = await self.db.execute(
            select(Reminder)
            .where(Reminder.sent.is_(False), Reminder.remind_at > now)
            .order_by(Reminder.remind_at),
        )
        return list(result.scalars().all())

    async def get_overdue_pending_tasks(self) -> list[Task]:
        now = datetime.now(UTC)
        result = await self.db.execute(
            select(Task).where(
                Task.status == TaskStatus.PENDING,
                Task.scheduled_at < now,
            ),
        )
        return list(result.scalars().all())

    async def complete_past_due_tasks(
        self,
        *,
        actor_type: AuditActorType = AuditActorType.SYSTEM,
        actor_id: int | None = None,
        source: AuditSource = AuditSource.WORKER,
    ) -> int:
        """Mark pending tasks past scheduled_at as completed."""
        tasks = await self.get_overdue_pending_tasks()
        for task in tasks:
            await self.update_task_status(
                task=task,
                new_status=TaskStatus.COMPLETED,
                actor_type=actor_type,
                actor_id=actor_id,
                source=source,
            )
        return len(tasks)

    async def enqueue_calendar_sync(
        self,
        *,
        task_id: int,
        action: SyncAction,
        google_event_id: str | None = None,
    ) -> GoogleSyncQueue:
        entry = GoogleSyncQueue(
            task_id=task_id,
            action=action,
            status=SyncStatus.PENDING,
            next_retry_at=datetime.now(UTC) + timedelta(seconds=5),
            google_event_id=google_event_id,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def delete_old_tasks(self, *, months: int = 4) -> int:
        cutoff = datetime.now(UTC) - timedelta(days=months * 30)
        result = await self.db.execute(
            select(Task).where(Task.scheduled_at < cutoff),
        )
        tasks = list(result.scalars().all())
        for task in tasks:
            await remove_task(self.db, task.id)
            await self.db.delete(task)
        await self.db.flush()
        return len(tasks)

    async def _count(self, model: type, *conditions: object) -> int:
        query = select(func.count()).select_from(model)
        for cond in conditions:
            query = query.where(cond)
        result = await self.db.execute(query)
        return result.scalar_one()


# Backward-compatible module-level helpers for todobot and workers.


async def create_task(db: AsyncSession, **kwargs: object) -> Task:
    return await TaskService(db).create_task(**kwargs)  # type: ignore[arg-type]


async def create_reminder(db: AsyncSession, **kwargs: object) -> Reminder:
    return await TaskService(db).create_reminder(**kwargs)  # type: ignore[arg-type]


async def update_task_status(db: AsyncSession, **kwargs: object) -> Task:
    return await TaskService(db).update_task_status(**kwargs)  # type: ignore[arg-type]


async def change_status(db: AsyncSession, **kwargs: object) -> Task:
    return await TaskService(db).change_status(**kwargs)  # type: ignore[arg-type]


async def reschedule_task(db: AsyncSession, **kwargs: object) -> Task:
    return await TaskService(db).reschedule_task(**kwargs)  # type: ignore[arg-type]


async def create_with_sync(db: AsyncSession, **kwargs: object) -> Task:
    return await TaskService(db).create_with_sync(**kwargs)  # type: ignore[arg-type]


async def get_task(db: AsyncSession, *, task_id: int) -> Task | None:
    return await TaskService(db).get_task(task_id=task_id)


async def get_pending_tasks(db: AsyncSession, **kwargs: object) -> list[Task]:
    return await TaskService(db).get_pending_tasks(**kwargs)  # type: ignore[arg-type]


async def get_unsent_reminders(db: AsyncSession) -> list[Reminder]:
    return await TaskService(db).get_unsent_reminders()


async def get_overdue_pending_tasks(db: AsyncSession) -> list[Task]:
    return await TaskService(db).get_overdue_pending_tasks()


async def complete_past_due_tasks(db: AsyncSession, **kwargs: object) -> int:
    return await TaskService(db).complete_past_due_tasks(**kwargs)  # type: ignore[arg-type]


async def enqueue_calendar_sync(db: AsyncSession, **kwargs: object) -> GoogleSyncQueue:
    return await TaskService(db).enqueue_calendar_sync(**kwargs)  # type: ignore[arg-type]


async def delete_old_tasks(db: AsyncSession, **kwargs: object) -> int:
    return await TaskService(db).delete_old_tasks(**kwargs)  # type: ignore[arg-type]
