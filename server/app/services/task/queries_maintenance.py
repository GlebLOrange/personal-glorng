"""Worker-facing task queries and maintenance jobs."""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.db.documents.audit import AuditActorType, AuditSource
from app.db.documents.task import (
    Reminder,
    Task,
    TaskStatus,
)
from app.services.search_indexers.task import remove_task
from app.services.task.service import (
    _TASK_WORKER_BATCH_LIMIT,
    TaskServiceBase,
)


class TaskMaintenanceMixin(TaskServiceBase):
    if TYPE_CHECKING:
        # Provided by a sibling mixin on TaskService.
        async def update_task_status(
            self,
            *,
            task: Task,
            new_status: TaskStatus,
            actor_type: AuditActorType = AuditActorType.SYSTEM,
            actor_id: int | None = None,
            source: AuditSource = AuditSource.WORKER,
        ) -> Task: ...

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
