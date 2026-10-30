"""Task and reminder business logic."""

from datetime import UTC, datetime, timedelta

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
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
    def __init__(
        self,
        registry: DatabaseRegistry,
        audit_svc: AuditService | None = None,
    ) -> None:
        self.registry = registry
        # ponytail: default skips optional Postgres; HTTP injects AuditServiceDep.
        self._audit = audit_svc or AuditService(registry)

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
        # Always ping at event start; optional early heads-up when minutes > 0.
        await self.schedule_reminder_minutes_before(
            task_id=task.id,
            scheduled_at=scheduled_at,
            minutes_before=0,
        )
        if reminder_minutes and reminder_minutes > 0:
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
        q: str | None = None,
        sort: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> TaskListResponse:
        offset, limit = paginate_params(page, per_page)
        if status:
            try:
                TaskStatus(status)
            except ValueError as exc:
                raise ValidationError(f"Invalid task status: {status}") from exc
        if start is not None and end is not None and start >= end:
            raise ValidationError("start must be before end")
        search = q.strip() if q else None
        if search == "":
            search = None
        range_start = as_utc(start) if start is not None else None
        range_end = as_utc(end) if end is not None else None
        tasks = await self._tasks().list_admin(
            offset=offset,
            limit=limit,
            status=status,
            q=search,
            sort=sort,
            start=range_start,
            end=range_end,
        )
        total = await self._tasks().count_all(
            status=status,
            q=search,
            start=range_start,
            end=range_end,
        )
        items = [TaskResponse.model_validate(t) for t in tasks]
        safe_page = max(1, page)
        return build_paginated(
            items,
            total=total,
            page=safe_page,
            per_page=limit,
            response_cls=TaskListResponse,
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
        titles = await self._tasks().titles_by_ids(
            list({entry.task_id for entry in items_raw}),
        )
        items = [
            SyncQueueResponse.model_validate(entry).model_copy(
                update={"task_title": titles.get(entry.task_id)},
            )
            for entry in items_raw
        ]
        safe_page = max(1, page)
        return build_paginated(
            items,
            total=total,
            page=safe_page,
            per_page=limit,
            response_cls=SyncQueueListResponse,
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

    async def _kick_calendar_sync_drain(
        self,
        *,
        context: dict[str, object] | None = None,
    ) -> None:
        """Drain due sync rows in-process (works without Celery worker/eager)."""
        try:
            from app.workers.tasks import process_sync_queue

            await process_sync_queue()
        except Exception as exc:
            logger.warning(
                "Failed to kick calendar sync drain",
                error=exc,
                context=context or {},
            )

    async def retry_sync(self, task_id: int) -> int:
        items = await self._tasks().list_failed_sync_for_task(task_id)
        if not items:
            raise NotFoundError("No failed sync entries for this task")

        now = datetime.now(UTC)
        for item in items:
            item.status = SyncStatus.PENDING
            item.attempts = 0
            item.next_retry_at = now
            await self._tasks().update_sync(item)

        await self._kick_calendar_sync_drain(context={"task_id": task_id})
        return len(items)

    async def process_sync_queue_now(self) -> int:
        """Arm pending sync rows and kick drain (admin Sync now)."""
        now = datetime.now(UTC)
        pending = await self._tasks().list_pending_sync(limit=_TASK_WORKER_BATCH_LIMIT)
        for item in pending:
            item.next_retry_at = now
            await self._tasks().update_sync(item)

        # process_sync_queue drains 10 per tick; loop kicks until idle or capped.
        max_kicks = max(1, (len(pending) // 10) + 1)
        for _ in range(max_kicks):
            await self._kick_calendar_sync_drain(context={"armed": len(pending)})
            due = await self._tasks().list_pending_sync_due(
                now=datetime.now(UTC),
                limit=1,
            )
            if not due:
                break
        return len(pending)

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

    async def get_closest_pending_tasks(
        self,
        *,
        telegram_user_id: int,
        limit: int = 7,
    ) -> list[Task]:
        """Pending tasks closest to now (upcoming and overdue), capped."""
        return await self._tasks().list_closest_pending(
            telegram_user_id,
            now=datetime.now(UTC),
            limit=limit,
        )

    async def sync_calendar_for_telegram_user(
        self,
        *,
        telegram_user_id: int,
    ) -> int:
        """Enqueue missing CREATE rows for this user and drain their pending sync."""
        if self.registry.credentials is None:
            return 0
        cred = await self.registry.credentials.get_google_for_telegram_user(
            telegram_user_id,
        )
        if cred is None:
            return 0

        tasks = await self.get_pending_tasks(
            telegram_user_id=telegram_user_id,
            limit=_TASK_WORKER_BATCH_LIMIT,
        )
        if not tasks:
            return 0

        task_ids = [task.id for task in tasks]
        pending = await self._tasks().list_pending_sync_for_task_ids(
            task_ids,
            limit=_TASK_WORKER_BATCH_LIMIT,
        )
        pending_task_ids = {item.task_id for item in pending}

        now = datetime.now(UTC)
        for item in pending:
            item.next_retry_at = now
            await self._tasks().update_sync(item)

        enqueued = 0
        for task in tasks:
            if task.google_event_id is not None:
                continue
            if task.id in pending_task_ids:
                continue
            await self.enqueue_calendar_sync(
                task_id=task.id,
                action=SyncAction.CREATE,
            )
            enqueued += 1

        armed = len(pending)
        # process_sync_queue drains 10 per tick; kick until this user's queue is idle.
        max_kicks = max(1, ((armed + enqueued) // 10) + 1)
        for _ in range(max_kicks):
            await self._kick_calendar_sync_drain(
                context={"telegram_user_id": telegram_user_id, "armed": armed},
            )
            remaining = await self._tasks().list_pending_sync_for_task_ids(
                task_ids,
                limit=1,
            )
            if not remaining:
                break
            item = remaining[0]
            if item.next_retry_at and item.next_retry_at > datetime.now(UTC):
                break
            item.next_retry_at = datetime.now(UTC)
            await self._tasks().update_sync(item)

        return armed + enqueued

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
            next_retry_at=datetime.now(UTC),
            google_event_id=google_event_id,
        )
        entry = await self._tasks().enqueue_sync(entry)
        await self._kick_calendar_sync_drain(
            context={"task_id": task_id, "queue_id": entry.id},
        )
        return entry

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


async def update_task_details(registry: DatabaseRegistry, **kwargs: object) -> Task:
    return await TaskService(registry).update_task_details(**kwargs)  # type: ignore[arg-type]


async def create_with_sync(registry: DatabaseRegistry, **kwargs: object) -> Task:
    return await TaskService(registry).create_with_sync(**kwargs)  # type: ignore[arg-type]


async def get_task(registry: DatabaseRegistry, *, task_id: int) -> Task | None:
    return await TaskService(registry).get_task(task_id=task_id)


async def get_pending_tasks(registry: DatabaseRegistry, **kwargs: object) -> list[Task]:
    return await TaskService(registry).get_pending_tasks(**kwargs)  # type: ignore[arg-type]


async def get_closest_pending_tasks(
    registry: DatabaseRegistry,
    **kwargs: object,
) -> list[Task]:
    return await TaskService(registry).get_closest_pending_tasks(
        **kwargs,  # type: ignore[arg-type]
    )


async def sync_calendar_for_telegram_user(
    registry: DatabaseRegistry,
    **kwargs: object,
) -> int:
    return await TaskService(registry).sync_calendar_for_telegram_user(
        **kwargs,  # type: ignore[arg-type]
    )


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
