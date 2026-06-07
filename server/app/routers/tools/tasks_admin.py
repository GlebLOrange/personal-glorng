"""Todobot task admin API. Default: `tasks:read`; writes: `tasks:write`."""

from fastapi import APIRouter, Depends

from app.core.deps import AuthorizedUser, DbSession, require_capability
from app.core.exceptions import ValidationError
from app.db.models.audit_event import AuditActorType, AuditSource
from app.db.models.google_sync_queue import SyncAction
from app.openapi import requires_capability
from app.schemas.common import MessageResponse
from app.schemas.task import (
    SyncQueueResponse,
    TaskCreate,
    TaskDetailResponse,
    TaskResponse,
    TaskStatsResponse,
)
from app.schemas.task_intake import TaskIntakeResponse
from app.services.task import TaskService
from app.services.task_intake import TaskIntakeService
from app.settings import get_settings

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(require_capability("tasks", "read"))],
)


@router.post(
    "",
    response_model=TaskResponse,
    summary="Create task",
    description=requires_capability("tasks", "write"),
    dependencies=[Depends(require_capability("tasks", "write"))],
)
async def create_task(
    data: TaskCreate,
    db: DbSession,
    user: AuthorizedUser,
) -> TaskResponse:
    settings = get_settings()
    telegram_user_id = data.telegram_user_id or settings.TELEGRAM_ALLOWED_USER_ID
    if not telegram_user_id:
        raise ValidationError(
            "telegram_user_id is required (set TELEGRAM_ALLOWED_USER_ID)",
        )

    svc = TaskService(db)
    task = await svc.create_task(
        telegram_user_id=telegram_user_id,
        title=data.title,
        scheduled_at=data.scheduled_at,
        description=data.description,
        location=data.location,
        source=AuditSource.WEB_ADMIN,
        actor_type=AuditActorType.USER,
        actor_id=user.id,
    )
    await svc.enqueue_calendar_sync(task_id=task.id, action=SyncAction.CREATE)
    await db.commit()
    return TaskResponse.model_validate(task)


@router.get(
    "",
    response_model=list[TaskResponse],
    summary="List tasks",
    description=requires_capability("tasks", "read"),
)
async def list_tasks(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
) -> list[TaskResponse]:
    svc = TaskService(db)
    return await svc.list_tasks(page=page, per_page=per_page, status=status)


@router.get(
    "/stats",
    response_model=TaskStatsResponse,
    summary="Get task statistics",
    description=requires_capability("tasks", "read"),
)
async def task_stats(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
) -> TaskStatsResponse:
    return await TaskService(db).task_stats()


@router.get(
    "/intakes",
    response_model=list[TaskIntakeResponse],
    summary="List task intakes",
    description=requires_capability("tasks", "read"),
)
async def list_intakes(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
) -> list[TaskIntakeResponse]:
    return await TaskIntakeService(db).list_intakes(page=page, per_page=per_page)


@router.get(
    "/sync-queue",
    response_model=list[SyncQueueResponse],
    summary="List calendar sync queue",
    description=requires_capability("tasks", "read"),
)
async def list_sync_queue(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
) -> list[SyncQueueResponse]:
    return await TaskService(db).list_sync_queue(page=page, per_page=per_page)


@router.get(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Get task detail",
    description=requires_capability("tasks", "read"),
)
async def task_detail(
    task_id: int,
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
) -> TaskDetailResponse:
    return await TaskService(db).task_detail(task_id)


@router.post(
    "/{task_id}/retry-sync",
    response_model=MessageResponse,
    summary="Retry calendar sync",
    description=requires_capability("tasks", "write"),
    dependencies=[Depends(require_capability("tasks", "write"))],
)
async def retry_sync(
    task_id: int,
    db: DbSession,
    _user: AuthorizedUser,
) -> MessageResponse:
    count = await TaskService(db).retry_sync(task_id)
    return MessageResponse(message=f"Retrying {count} sync entries")
