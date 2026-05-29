"""Admin API for viewing and managing todobot tasks."""

from fastapi import APIRouter, Depends

from app.core.deps import AdminUser, DbSession, require_admin
from app.schemas.common import MessageResponse
from app.schemas.task import (
    SyncQueueResponse,
    TaskDetailResponse,
    TaskResponse,
    TaskStatsResponse,
)
from app.services.task import TaskService

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
    svc = TaskService(db)
    return await svc.list_tasks(page=page, per_page=per_page, status=status)


@router.get("/stats", response_model=TaskStatsResponse)
async def task_stats(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> TaskStatsResponse:
    return await TaskService(db).task_stats()


@router.get("/sync-queue", response_model=list[SyncQueueResponse])
async def list_sync_queue(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
) -> list[SyncQueueResponse]:
    return await TaskService(db).list_sync_queue(page=page, per_page=per_page)


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def task_detail(
    task_id: int,
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> TaskDetailResponse:
    return await TaskService(db).task_detail(task_id)


@router.post("/{task_id}/retry-sync", response_model=MessageResponse)
async def retry_sync(
    task_id: int,
    db: DbSession,
    user: AdminUser,
) -> MessageResponse:
    count = await TaskService(db).retry_sync(task_id)
    return MessageResponse(message=f"Retrying {count} sync entries")
