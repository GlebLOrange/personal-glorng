"""Task and reminder business logic."""

from datetime import UTC, datetime, timedelta

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import logger
from app.core.pagination import build_paginated
from app.core.utils import DEFAULT_PER_PAGE, as_utc, paginate_params
from app.db.documents.audit import AuditActorType, AuditSource
from app.db.documents.task import (
    GoogleSyncQueue,
    Reminder,
    SyncAction,
    SyncStatus,
    Task,
    TaskStatus,
)
from app.db.registry import DatabaseRegistry
from app.schemas.task import (
    ReminderResponse,
    StatusHistoryResponse,
    SyncQueueListResponse,
    SyncQueueResponse,
    TaskDetailResponse,
    TaskListResponse,
    TaskResponse,
    TaskStatsResponse,
    TaskTextFields,
)
from app.services.audit import AuditService, domain_event
from app.services.search_indexers.task import index_task, remove_task

_TASK_WORKER_BATCH_LIMIT = 100


class TaskService:
    def __init__(self, registry: DatabaseRegistry) -> None:
        self.registry = registry

    def _tasks(self):
        if self.registry.tasks is None:
            msg = "Tasks repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.tasks

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
        task = await self._tasks().insert(task)
        await index_task(self.registry, task)
        logger.info("Task created", context={"task_id": task.id, "title": fields.title})

        await AuditService(self.registry).record(
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
        return await self._tasks().create_reminder(
            task_id=task_id,
            remind_at=remind_at,
            job_id=job_id,
        )

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
        task = await self._tasks().replace(task)
        await self._tasks().add_status_history(
            task_id=task.id,
            old_status=old_status.value,
            new_status=new_status.value,
        )
        await index_task(self.registry, task)

        logger.debug(
            "Task status updated",
            context={
                "task_id": task.id,
                "old": old_status.value,
                "new": new_status.value,
            },
        )

        await AuditService(self.registry).record(
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
        fields: dict[str, object] = {"scheduled_at": as_utc(scheduled_at)}
        if task.status == TaskStatus.POSTPONED:
            fields["status"] = TaskStatus.PENDING.value
        task = await self._tasks().update_fields(task_id, **fields)
        await index_task(self.registry, task)

        await AuditService(self.registry).record(
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
        await schedule_reminder(self.registry, reminder)
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
        return await self._tasks().get_or_none(task_id)

    async def list_tasks(
        self,
        *,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
        status: str | None = None,
    ) -> TaskListResponse:
        offset, limit = paginate_params(page, per_page)
        if status:
            try:
                TaskStatus(status)
            except ValueError as exc:
                raise ValidationError(f"Invalid task status: {status}") from exc
        tasks = await self._tasks().list_admin(
            offset=offset,
            limit=limit,
            status=status,
        )
        total = await self._tasks().count_all(status=status)
        items = [TaskResponse.model_validate(t) for t in tasks]
        safe_page = max(1, page)
        return build_paginated(
            items,
            total=total,
            page=safe_page,
            per_page=limit,
        )

    async def task_stats(self) -> TaskStatsResponse:
        total = await self._tasks().count_all()
        pending = await self._tasks().count_all(status=TaskStatus.PENDING.value)
        completed = await self._tasks().count_all(status=TaskStatus.COMPLETED.value)
        failed_syncs = await self._tasks().count_sync_by_status(SyncStatus.FAILED)
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
        per_page: int = DEFAULT_PER_PAGE,
    ) -> SyncQueueListResponse:
        offset, limit = paginate_params(page, per_page)
        items_raw = await self._tasks().list_sync_queue(offset=offset, limit=limit)
        total = await self._tasks().count_sync_queue()
        items = [SyncQueueResponse.model_validate(q) for q in items_raw]
        safe_page = max(1, page)
        return build_paginated(
            items,
            total=total,
            page=safe_page,
            per_page=limit,
        )

    async def task_detail(self, task_id: int) -> TaskDetailResponse:
        task = await self.get_task(task_id=task_id)
        if not task:
            raise NotFoundError("Task not found")

        reminders = await self._tasks().list_reminders_for_task(task_id)
        history = await self._tasks().list_status_history(task_id)

        return TaskDetailResponse(
            **TaskResponse.model_validate(task).model_dump(),
            reminders=[ReminderResponse.model_validate(r) for r in reminders],
            status_history=[StatusHistoryResponse.model_validate(h) for h in history],
        )

    async def retry_sync(self, task_id: int) -> int:
        items = await self._tasks().list_failed_sync_for_task(task_id)
        if not items:
            raise NotFoundError("No failed sync entries for this task")

        for item in items:
            item.status = SyncStatus.PENDING
            item.attempts = 0
            item.next_retry_at = datetime.now(UTC) + timedelta(seconds=5)
            await self._tasks().update_sync(item)

        return len(items)

    async def get_pending_tasks(
        self,
        *,
        telegram_user_id: int,
        limit: int = 20,
    ) -> list[Task]:
        return await self._tasks().list_for_user(
            telegram_user_id,
            limit=limit,
            status=TaskStatus.PENDING,
        )

    async def get_unsent_reminders(
        self,
        *,
        limit: int = _TASK_WORKER_BATCH_LIMIT,
        offset: int = 0,
    ) -> list[Reminder]:
        return await self._tasks().list_unsent_future_reminders(
            now=datetime.now(UTC),
            limit=limit,
            offset=offset,
        )

    async def get_overdue_pending_tasks(
        self,
        *,
        limit: int = _TASK_WORKER_BATCH_LIMIT,
    ) -> list[Task]:
        return await self._tasks().list_overdue_pending(
            now=datetime.now(UTC),
            limit=limit,
        )

    async def complete_past_due_tasks(
        self,
        *,
        actor_type: AuditActorType = AuditActorType.SYSTEM,
        actor_id: int | None = None,
        source: AuditSource = AuditSource.WORKER,
    ) -> int:
        """Mark pending tasks past scheduled_at as completed."""
        # ponytail: process one bounded batch per tick; switch to cursor/bulk status
        # updates if overdue-task backlogs become normal.
        tasks = await self.get_overdue_pending_tasks(limit=_TASK_WORKER_BATCH_LIMIT)
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
            id=0,
            task_id=task_id,
            action=action,
            status=SyncStatus.PENDING,
            next_retry_at=datetime.now(UTC) + timedelta(seconds=5),
            google_event_id=google_event_id,
        )
        return await self._tasks().enqueue_sync(entry)

    async def delete_old_tasks(self, *, months: int = 4) -> int:
        cutoff = datetime.now(UTC) - timedelta(days=months * 30)
        # ponytail: bounded cleanup keeps worker ticks short; use cursor/bulk delete
        # when retention cleanup needs to drain large historical backlogs.
        tasks = await self._tasks().list_older_than(
            cutoff=cutoff,
            limit=_TASK_WORKER_BATCH_LIMIT,
        )
        for task in tasks:
            await remove_task(self.registry, task.id)
            await self._tasks().delete(task.id)
        return len(tasks)


# Backward-compatible module-level helpers for todobot and workers.


async def create_task(registry: DatabaseRegistry, **kwargs: object) -> Task:
    return await TaskService(registry).create_task(**kwargs)  # type: ignore[arg-type]


async def create_reminder(registry: DatabaseRegistry, **kwargs: object) -> Reminder:
    return await TaskService(registry).create_reminder(**kwargs)  # type: ignore[arg-type]


async def update_task_status(registry: DatabaseRegistry, **kwargs: object) -> Task:
    return await TaskService(registry).update_task_status(**kwargs)  # type: ignore[arg-type]


async def change_status(registry: DatabaseRegistry, **kwargs: object) -> Task:
    return await TaskService(registry).change_status(**kwargs)  # type: ignore[arg-type]


async def reschedule_task(registry: DatabaseRegistry, **kwargs: object) -> Task:
    return await TaskService(registry).reschedule_task(**kwargs)  # type: ignore[arg-type]


async def create_with_sync(registry: DatabaseRegistry, **kwargs: object) -> Task:
    return await TaskService(registry).create_with_sync(**kwargs)  # type: ignore[arg-type]


async def get_task(registry: DatabaseRegistry, *, task_id: int) -> Task | None:
    return await TaskService(registry).get_task(task_id=task_id)


async def get_pending_tasks(registry: DatabaseRegistry, **kwargs: object) -> list[Task]:
    return await TaskService(registry).get_pending_tasks(**kwargs)  # type: ignore[arg-type]


async def get_unsent_reminders(
    registry: DatabaseRegistry,
    *,
    limit: int = _TASK_WORKER_BATCH_LIMIT,
    offset: int = 0,
) -> list[Reminder]:
    return await TaskService(registry).get_unsent_reminders(
        limit=limit,
        offset=offset,
    )


async def get_overdue_pending_tasks(registry: DatabaseRegistry) -> list[Task]:
    return await TaskService(registry).get_overdue_pending_tasks()


async def complete_past_due_tasks(registry: DatabaseRegistry, **kwargs: object) -> int:
    return await TaskService(registry).complete_past_due_tasks(**kwargs)  # type: ignore[arg-type]


async def enqueue_calendar_sync(
    registry: DatabaseRegistry,
    **kwargs: object,
) -> GoogleSyncQueue:
    return await TaskService(registry).enqueue_calendar_sync(**kwargs)  # type: ignore[arg-type]


async def delete_old_tasks(registry: DatabaseRegistry, **kwargs: object) -> int:
    return await TaskService(registry).delete_old_tasks(**kwargs)  # type: ignore[arg-type]
