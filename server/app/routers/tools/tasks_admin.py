"""Todobot task admin API. Default: `tasks:read`; writes: `tasks:write`."""

from fastapi import APIRouter, Depends

from app.core.deps import (
    AdminUser,
    AppSettings,
    AuthorizedUser,
    DbSession,
    TaskIntakeServiceDep,
    TaskServiceDep,
    require_capability,
)
from app.core.exceptions import ValidationError
from app.db.models.audit_event import AuditActorType, AuditSource
from app.schemas.common import MessageResponse
from app.schemas.task import (
    ReminderResponse,
    SyncQueueResponse,
    TaskCreate,
    TaskDetailResponse,
    TaskReminderCreate,
    TaskReschedule,
    TaskResponse,
    TaskStatsResponse,
    TaskStatusUpdate,
)
from app.schemas.task_intake import TaskIntakeResponse
from app.settings import Settings

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(require_capability("tasks", "read"))],
)


def _resolve_telegram_user_id(data: TaskCreate, settings: Settings) -> int:
    telegram_user_id = data.telegram_user_id or settings.TELEGRAM_ALLOWED_USER_ID
    if not telegram_user_id:
        raise ValidationError(
            "telegram_user_id is required (set TELEGRAM_ALLOWED_USER_ID)",
        )
    return telegram_user_id


@router.post("", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    db: DbSession,
    user: AdminUser,
    settings: AppSettings,
    svc: TaskServiceDep,
) -> TaskResponse:
    task = await svc.create_with_sync(
        telegram_user_id=_resolve_telegram_user_id(data, settings),
        title=data.title,
        scheduled_at=data.scheduled_at,
        description=data.description,
        location=data.location,
        reminder_minutes=data.reminder_minutes,
        source=AuditSource.WEB_ADMIN,
        actor_type=AuditActorType.USER,
        actor_id=user.id,
    )
    await db.commit()
    return TaskResponse.model_validate(task)


@router.get(
    "",
    response_model=list[TaskResponse],
    summary="List tasks",
    description=requires_capability("tasks", "read"),
)
async def list_tasks(
    svc: TaskServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
) -> list[TaskResponse]:
    return await svc.list_tasks(page=page, per_page=per_page, status=status)


@router.get(
    "/stats",
    response_model=TaskStatsResponse,
    summary="Get task statistics",
    description=requires_capability("tasks", "read"),
)
async def task_stats(
    svc: TaskServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> TaskStatsResponse:
    return await svc.task_stats()


@router.get(
    "/intakes",
    response_model=list[TaskIntakeResponse],
    summary="List task intakes",
    description=requires_capability("tasks", "read"),
)
async def list_intakes(
    svc: TaskIntakeServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
) -> list[TaskIntakeResponse]:
    return await svc.list_intakes(page=page, per_page=per_page)


@router.get(
    "/sync-queue",
    response_model=list[SyncQueueResponse],
    summary="List calendar sync queue",
    description=requires_capability("tasks", "read"),
)
async def list_sync_queue(
    svc: TaskServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
) -> list[SyncQueueResponse]:
    return await svc.list_sync_queue(page=page, per_page=per_page)


@router.get(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Get task detail",
    description=requires_capability("tasks", "read"),
)
async def task_detail(
    task_id: int,
    svc: TaskServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> TaskDetailResponse:
    return await svc.task_detail(task_id)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    data: TaskStatusUpdate,
    db: DbSession,
    user: AdminUser,
    svc: TaskServiceDep,
) -> TaskResponse:
    task = await svc.change_status(
        task_id=task_id,
        new_status=data.status,
        source=AuditSource.WEB_ADMIN,
        actor_type=AuditActorType.USER,
        actor_id=user.id,
    )
    await db.commit()
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def reschedule_task(
    task_id: int,
    data: TaskReschedule,
    db: DbSession,
    user: AdminUser,
    svc: TaskServiceDep,
) -> TaskResponse:
    task = await svc.reschedule_task(
        task_id=task_id,
        scheduled_at=data.scheduled_at,
        source=AuditSource.WEB_ADMIN,
        actor_type=AuditActorType.USER,
        actor_id=user.id,
    )
    await db.commit()
    return TaskResponse.model_validate(task)


@router.post("/{task_id}/reminders", response_model=ReminderResponse)
async def add_task_reminder(
    task_id: int,
    data: TaskReminderCreate,
    db: DbSession,
    _user: AdminUser,
    svc: TaskServiceDep,
) -> ReminderResponse:
    task = await svc.require_task(task_id=task_id)
    reminder = await svc.schedule_reminder_minutes_before(
        task_id=task.id,
        scheduled_at=task.scheduled_at,
        minutes_before=data.minutes_before,
    )
    if not reminder:
        raise ValidationError("Reminder time must be in the future")
    await db.commit()
    return ReminderResponse.model_validate(reminder)


@router.post("/{task_id}/retry-sync", response_model=MessageResponse)
async def retry_sync(
    task_id: int,
    db: DbSession,
    _user: AdminUser,
    svc: TaskServiceDep,
) -> MessageResponse:
    count = await svc.retry_sync(task_id)
    await db.commit()
    return MessageResponse(message=f"Retrying {count} sync entries")
