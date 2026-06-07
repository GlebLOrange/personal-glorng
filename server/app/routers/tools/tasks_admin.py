"""Admin API for viewing and managing todobot tasks."""

from fastapi import APIRouter, Depends

from app.core.deps import AuthorizedUser, DbSession, require_capability
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
from app.services.task import TaskService
from app.services.task_intake import TaskIntakeService
from app.settings import get_settings

router = APIRouter(
    prefix="/tasks",
    dependencies=[Depends(require_capability("tasks", "read"))],
)


def _resolve_telegram_user_id(data: TaskCreate) -> int:
    settings = get_settings()
    telegram_user_id = data.telegram_user_id or settings.TELEGRAM_ALLOWED_USER_ID
    if not telegram_user_id:
        raise ValidationError(
            "telegram_user_id is required (set TELEGRAM_ALLOWED_USER_ID)",
        )
    return telegram_user_id


@router.post(
    "",
    response_model=TaskResponse,
    dependencies=[Depends(require_capability("tasks", "write"))],
)
async def create_task(
    data: TaskCreate,
    db: DbSession,
    user: AuthorizedUser,
) -> TaskResponse:
    svc = TaskService(db)
    task = await svc.create_with_sync(
        telegram_user_id=_resolve_telegram_user_id(data),
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


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
) -> list[TaskResponse]:
    return await TaskService(db).list_tasks(page=page, per_page=per_page, status=status)


@router.get("/stats", response_model=TaskStatsResponse)
async def task_stats(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
) -> TaskStatsResponse:
    return await TaskService(db).task_stats()


@router.get("/intakes", response_model=list[TaskIntakeResponse])
async def list_intakes(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
) -> list[TaskIntakeResponse]:
    return await TaskIntakeService(db).list_intakes(page=page, per_page=per_page)


@router.get("/sync-queue", response_model=list[SyncQueueResponse])
async def list_sync_queue(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
) -> list[SyncQueueResponse]:
    return await TaskService(db).list_sync_queue(page=page, per_page=per_page)


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def task_detail(
    task_id: int,
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
) -> TaskDetailResponse:
    return await TaskService(db).task_detail(task_id)


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    dependencies=[Depends(require_capability("tasks", "write"))],
)
async def update_task_status(
    task_id: int,
    data: TaskStatusUpdate,
    db: DbSession,
    user: AuthorizedUser,
) -> TaskResponse:
    task = await TaskService(db).change_status(
        task_id=task_id,
        new_status=data.status,
        source=AuditSource.WEB_ADMIN,
        actor_type=AuditActorType.USER,
        actor_id=user.id,
    )
    await db.commit()
    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    dependencies=[Depends(require_capability("tasks", "write"))],
)
async def reschedule_task(
    task_id: int,
    data: TaskReschedule,
    db: DbSession,
    user: AuthorizedUser,
) -> TaskResponse:
    task = await TaskService(db).reschedule_task(
        task_id=task_id,
        scheduled_at=data.scheduled_at,
        source=AuditSource.WEB_ADMIN,
        actor_type=AuditActorType.USER,
        actor_id=user.id,
    )
    await db.commit()
    return TaskResponse.model_validate(task)


@router.post(
    "/{task_id}/reminders",
    response_model=ReminderResponse,
    dependencies=[Depends(require_capability("tasks", "write"))],
)
async def add_task_reminder(
    task_id: int,
    data: TaskReminderCreate,
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
) -> ReminderResponse:
    svc = TaskService(db)
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


@router.post(
    "/{task_id}/retry-sync",
    response_model=MessageResponse,
    dependencies=[Depends(require_capability("tasks", "write"))],
)
async def retry_sync(
    task_id: int,
    db: DbSession,
    _user: AuthorizedUser,
) -> MessageResponse:
    count = await TaskService(db).retry_sync(task_id)
    await db.commit()
    return MessageResponse(message=f"Retrying {count} sync entries")
