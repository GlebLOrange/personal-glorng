"""Admin API for viewing and managing todobot tasks."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import AdminUser, DbSession, require_admin
from app.core.utils import paginate_params
from app.models.google_sync_queue import GoogleSyncQueue, SyncStatus
from app.models.reminder import Reminder
from app.models.task import Task, TaskStatus
from app.models.task_status_history import TaskStatusHistory
from app.schemas.common import MessageResponse
from app.schemas.task import (
    ReminderResponse,
    StatusHistoryResponse,
    SyncQueueResponse,
    TaskDetailResponse,
    TaskResponse,
    TaskStatsResponse,
)

router = APIRouter(
    prefix="/tasks",
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
) -> list[TaskResponse]:
    offset, limit = paginate_params(page, per_page)
    query = select(Task).order_by(Task.created_at.desc())
    if status:
        query = query.where(Task.status == status)
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return [TaskResponse.model_validate(t) for t in result.scalars().all()]


@router.get("/stats", response_model=TaskStatsResponse)
async def task_stats(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> TaskStatsResponse:
    total = await _count(db, Task)
    pending = await _count(db, Task, Task.status == TaskStatus.PENDING)
    completed = await _count(db, Task, Task.status == TaskStatus.COMPLETED)
    failed_syncs = await _count(
        db,
        GoogleSyncQueue,
        GoogleSyncQueue.status == SyncStatus.FAILED,
    )
    return TaskStatsResponse(
        pending=pending,
        completed=completed,
        total=total,
        failed_syncs=failed_syncs,
    )


@router.get("/sync-queue", response_model=list[SyncQueueResponse])
async def list_sync_queue(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
) -> list[SyncQueueResponse]:
    offset, limit = paginate_params(page, per_page)
    result = await db.execute(
        select(GoogleSyncQueue)
        .order_by(GoogleSyncQueue.created_at.desc())
        .offset(offset)
        .limit(limit),
    )
    return [SyncQueueResponse.model_validate(q) for q in result.scalars().all()]


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def task_detail(
    task_id: int,
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> TaskDetailResponse:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Task not found")

    reminders_result = await db.execute(
        select(Reminder)
        .where(Reminder.task_id == task_id)
        .order_by(Reminder.remind_at),
    )
    history_result = await db.execute(
        select(TaskStatusHistory)
        .where(TaskStatusHistory.task_id == task_id)
        .order_by(TaskStatusHistory.changed_at),
    )

    return TaskDetailResponse(
        **TaskResponse.model_validate(task).model_dump(),
        reminders=[
            ReminderResponse.model_validate(r) for r in reminders_result.scalars().all()
        ],
        status_history=[
            StatusHistoryResponse.model_validate(h)
            for h in history_result.scalars().all()
        ],
    )


@router.post("/{task_id}/retry-sync", response_model=MessageResponse)
async def retry_sync(
    task_id: int,
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> MessageResponse:
    result = await db.execute(
        select(GoogleSyncQueue).where(
            GoogleSyncQueue.task_id == task_id,
            GoogleSyncQueue.status == SyncStatus.FAILED,
        ),
    )
    items = list(result.scalars().all())
    if not items:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("No failed sync entries for this task")

    for item in items:
        item.status = SyncStatus.PENDING
        item.attempts = 0
        item.next_retry_at = datetime.now(UTC) + timedelta(seconds=5)
        db.add(item)

    await db.flush()
    return MessageResponse(message=f"Retrying {len(items)} sync entries")


async def _count(
    db: AsyncSession,
    model: type,
    *conditions: object,
) -> int:
    query = select(func.count()).select_from(model)
    for cond in conditions:
        query = query.where(cond)
    result = await db.execute(query)
    return result.scalar_one()
