"""Task create/update/reschedule/reminder mutations."""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.core.exceptions import ConflictError, ValidationError
from app.core.logging import logger
from app.core.utils import as_utc
from app.db.documents.audit import AuditActorType, AuditSource
from app.db.documents.task import (
    GoogleSyncQueue,
    Reminder,
    SyncAction,
    Task,
    TaskStatus,
)
from app.schemas.task import (
    TaskTextFields,
)
from app.services.audit import domain_event
from app.services.search_indexers.task import index_task
from app.services.task.service import (
    DEFAULT_EARLY_REMINDER_MINUTES,
    TaskServiceBase,
)


class TaskMutationsMixin(TaskServiceBase):
    if TYPE_CHECKING:
        # Provided by a sibling mixin on TaskService.
        async def enqueue_calendar_sync(
            self,
            *,
            task_id: int,
            action: SyncAction,
            google_event_id: str | None = None,
        ) -> GoogleSyncQueue: ...

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

        await self._audit.record(
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

        await self._audit.record(
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
        if task.google_event_id:
            await self.enqueue_calendar_sync(
                task_id=task.id,
                action=SyncAction.UPDATE,
                google_event_id=task.google_event_id,
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
        allow_future_complete: bool = False,
    ) -> Task:
        task = await self.require_task(task_id=task_id)
        if (
            new_status == TaskStatus.COMPLETED
            and not allow_future_complete
            and as_utc(task.scheduled_at) > datetime.now(UTC)
        ):
            raise ConflictError(
                "Cannot mark a future task as completed",
            )
        return await self.update_task_status(
            task=task,
            new_status=new_status,
            actor_type=actor_type,
            actor_id=actor_id,
            source=source,
        )

    async def update_task_details(
        self,
        *,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        location: str | None = None,
        actor_type: AuditActorType = AuditActorType.SYSTEM,
        actor_id: int | None = None,
        source: AuditSource = AuditSource.TODOBOT,
    ) -> Task:
        """Update title / notes / location without changing schedule."""
        fields: dict[str, object] = {}
        if title is not None:
            fields["title"] = title
        if description is not None:
            fields["description"] = description
        if location is not None:
            fields["location"] = location
        if not fields:
            return await self.require_task(task_id=task_id)
        task = await self._tasks().update_fields(task_id, **fields)
        await index_task(self.registry, task)
        await self._audit.record(
            domain_event(
                action="task.updated",
                actor_type=actor_type,
                actor_id=actor_id,
                source=source,
                resource_type="task",
                resource_id=task.id,
                metadata={"fields": sorted(fields)},
            ),
        )
        if task.google_event_id:
            await self.enqueue_calendar_sync(
                task_id=task.id,
                action=SyncAction.UPDATE,
                google_event_id=task.google_event_id,
            )
        return task

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

        await self._audit.record(
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
        # reminder_minutes kept for call-site compat; ignored — early offsets are static.
        _ = reminder_minutes
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
        # Always ping at event start + fixed early heads-ups (skip past offsets).
        await self.schedule_reminder_minutes_before(
            task_id=task.id,
            scheduled_at=scheduled_at,
            minutes_before=0,
        )
        for minutes_before in DEFAULT_EARLY_REMINDER_MINUTES:
            await self.schedule_reminder_minutes_before(
                task_id=task.id,
                scheduled_at=scheduled_at,
                minutes_before=minutes_before,
            )
        await self.enqueue_calendar_sync(task_id=task.id, action=SyncAction.CREATE)
        return task
