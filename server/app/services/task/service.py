"""Task service base: construction, lookups, listing, stats."""

from datetime import datetime

from app.core.exceptions import NotFoundError, ValidationError
from app.core.pagination import build_paginated
from app.core.utils import DEFAULT_PER_PAGE, as_utc, paginate_params
from app.db.documents.task import (
    SyncStatus,
    Task,
    TaskStatus,
)
from app.db.registry import DatabaseRegistry
from app.schemas.task import (
    ReminderResponse,
    StatusHistoryResponse,
    TaskDetailResponse,
    TaskListResponse,
    TaskResponse,
    TaskStatsResponse,
)
from app.services.audit import AuditService

_TASK_WORKER_BATCH_LIMIT = 100

# Static early Telegram + Calendar offsets; not user-configurable at create time.
DEFAULT_EARLY_REMINDER_MINUTES: tuple[int, ...] = (90, 60, 30)
STATIC_REMINDER_LABEL = "Reminders: 90 / 60 / 30 min before + at start"


class TaskServiceBase:
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
