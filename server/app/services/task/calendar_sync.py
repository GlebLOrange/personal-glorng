"""Google Calendar sync queue operations for tasks."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.core.exceptions import NotFoundError
from app.core.logging import logger
from app.core.pagination import build_paginated
from app.core.utils import DEFAULT_PER_PAGE, paginate_params
from app.db.documents.task import (
    GoogleSyncQueue,
    SyncAction,
    SyncStatus,
    Task,
)
from app.schemas.task import (
    SyncQueueListResponse,
    SyncQueueResponse,
)
from app.services.task.service import _TASK_WORKER_BATCH_LIMIT, TaskServiceBase


class TaskCalendarSyncMixin(TaskServiceBase):
    if TYPE_CHECKING:
        # Provided by a sibling mixin on TaskService.
        async def get_pending_tasks(
            self,
            *,
            telegram_user_id: int,
            limit: int = 20,
        ) -> list[Task]: ...

    async def list_sync_queue(
        self,
        *,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
        sort: str | None = None,
    ) -> SyncQueueListResponse:
        offset, limit = paginate_params(page, per_page)
        items_raw = await self._tasks().list_sync_queue(
            offset=offset,
            limit=limit,
            ascending=sort == "queued_asc",
        )
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
