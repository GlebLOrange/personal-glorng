"""Task and reminder business logic."""

from app.db.documents.task import GoogleSyncQueue, Reminder, Task
from app.db.registry import DatabaseRegistry
from app.services.task.calendar_sync import TaskCalendarSyncMixin
from app.services.task.mutations import TaskMutationsMixin
from app.services.task.queries_maintenance import TaskMaintenanceMixin
from app.services.task.service import (
    _TASK_WORKER_BATCH_LIMIT,
    DEFAULT_EARLY_REMINDER_MINUTES,
    STATIC_REMINDER_LABEL,
    TaskServiceBase,
)

__all__ = [
    "DEFAULT_EARLY_REMINDER_MINUTES",
    "STATIC_REMINDER_LABEL",
    "TaskService",
    "change_status",
    "complete_past_due_tasks",
    "create_reminder",
    "create_task",
    "create_with_sync",
    "delete_old_tasks",
    "enqueue_calendar_sync",
    "get_closest_pending_tasks",
    "get_overdue_pending_tasks",
    "get_pending_tasks",
    "get_task",
    "get_unsent_reminders",
    "reschedule_task",
    "sync_calendar_for_telegram_user",
    "update_task_details",
    "update_task_status",
]


class TaskService(
    TaskMutationsMixin,
    TaskCalendarSyncMixin,
    TaskMaintenanceMixin,
    TaskServiceBase,
):
    """Task façade assembled from focused mixins."""


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
