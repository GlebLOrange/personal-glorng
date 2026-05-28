"""Task and reminder business logic."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.db.models.google_sync_queue import GoogleSyncQueue, SyncAction, SyncStatus
from app.db.models.reminder import Reminder
from app.db.models.task import Task, TaskStatus
from app.db.models.task_status_history import TaskStatusHistory


async def create_task(
    db: AsyncSession,
    *,
    telegram_user_id: int,
    title: str,
    scheduled_at: str,
    description: str | None = None,
    location: str | None = None,
) -> Task:
    task = Task(
        telegram_user_id=telegram_user_id,
        title=title,
        description=description,
        location=location,
        scheduled_at=scheduled_at,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    logger.info("Task created", context={"task_id": task.id, "title": title})
    return task


async def create_reminder(
    db: AsyncSession,
    *,
    task_id: int,
    remind_at: datetime,
    arq_job_id: str | None = None,
) -> Reminder:
    reminder = Reminder(
        task_id=task_id,
        remind_at=remind_at,
        sent=False,
        arq_job_id=arq_job_id,
    )
    db.add(reminder)
    await db.flush()
    await db.refresh(reminder)
    return reminder


async def update_task_status(
    db: AsyncSession,
    *,
    task: Task,
    new_status: TaskStatus,
) -> Task:
    """Update status and record history."""
    old_status = task.status
    task.status = new_status
    db.add(task)

    history = TaskStatusHistory(
        task_id=task.id,
        old_status=old_status.value,
        new_status=new_status.value,
    )
    db.add(history)
    await db.flush()

    logger.info(
        "Task status updated",
        context={
            "task_id": task.id,
            "old": old_status.value,
            "new": new_status.value,
        },
    )
    return task


async def get_task(db: AsyncSession, *, task_id: int) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def get_pending_tasks(
    db: AsyncSession,
    *,
    telegram_user_id: int,
    limit: int = 20,
) -> list[Task]:
    result = await db.execute(
        select(Task)
        .where(
            Task.telegram_user_id == telegram_user_id,
            Task.status == TaskStatus.PENDING,
        )
        .order_by(Task.scheduled_at)
        .limit(limit),
    )
    return list(result.scalars().all())


async def get_unsent_reminders(db: AsyncSession) -> list[Reminder]:
    """Get all unsent reminders with future remind_at."""
    now = datetime.now(UTC)
    result = await db.execute(
        select(Reminder)
        .where(Reminder.sent.is_(False), Reminder.remind_at > now)
        .order_by(Reminder.remind_at),
    )
    return list(result.scalars().all())


async def get_overdue_pending_tasks(db: AsyncSession) -> list[Task]:
    """Tasks past scheduled time that are still pending."""
    now = datetime.now(UTC).isoformat()
    result = await db.execute(
        select(Task).where(
            Task.status == TaskStatus.PENDING,
            Task.scheduled_at < now,
        ),
    )
    return list(result.scalars().all())


async def enqueue_calendar_sync(
    db: AsyncSession,
    *,
    task_id: int,
    action: SyncAction,
    google_event_id: str | None = None,
) -> GoogleSyncQueue:
    entry = GoogleSyncQueue(
        task_id=task_id,
        action=action,
        status=SyncStatus.PENDING,
        next_retry_at=datetime.now(UTC) + timedelta(seconds=5),
        google_event_id=google_event_id,
    )
    db.add(entry)
    await db.flush()
    return entry


async def delete_old_tasks(
    db: AsyncSession,
    *,
    months: int = 4,
) -> int:
    """Delete tasks older than given months. Returns count deleted."""
    cutoff = (datetime.now(UTC) - timedelta(days=months * 30)).isoformat()
    result = await db.execute(
        select(Task).where(Task.scheduled_at < cutoff),
    )
    tasks = list(result.scalars().all())
    for task in tasks:
        await db.delete(task)
    await db.flush()
    return len(tasks)
