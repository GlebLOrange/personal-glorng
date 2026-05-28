"""Enqueue and supersede ARQ reminder jobs."""

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.db.models.reminder import Reminder
from app.workers.pool import abort_job, enqueue_job


def _as_utc(value: datetime) -> datetime:
    """Normalize DB datetimes to UTC-aware for comparisons."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


async def supersede_unsent_reminders(
    db: AsyncSession,
    task_id: int,
    *,
    exclude_id: int | None = None,
) -> None:
    """Abort and delete unsent future reminders for a task."""
    now = datetime.now(UTC)
    query = select(Reminder).where(
        Reminder.task_id == task_id,
        Reminder.sent.is_(False),
    )
    if exclude_id is not None:
        query = query.where(Reminder.id != exclude_id)

    result = await db.execute(query)
    reminders = [
        reminder
        for reminder in result.scalars().all()
        if _as_utc(reminder.remind_at) > now
    ]
    for reminder in reminders:
        if reminder.arq_job_id:
            await abort_job(reminder.arq_job_id)

    if not reminders:
        return

    reminder_ids = [reminder.id for reminder in reminders]
    await db.execute(delete(Reminder).where(Reminder.id.in_(reminder_ids)))
    await db.flush()
    logger.info(
        "Superseded unsent reminders",
        context={"task_id": task_id, "count": len(reminder_ids)},
    )


async def schedule_reminder(db: AsyncSession, reminder: Reminder) -> Reminder:
    """Enqueue send_reminder for a DB reminder row."""
    now = datetime.now(UTC)
    remind_at = _as_utc(reminder.remind_at)
    if reminder.sent or remind_at <= now:
        return reminder

    job_id = await enqueue_job(
        "send_reminder",
        reminder.id,
        _defer_until=remind_at,
    )
    if job_id:
        reminder.arq_job_id = job_id
        db.add(reminder)
        await db.flush()
        logger.info(
            "Reminder scheduled",
            context={"reminder_id": reminder.id, "job_id": job_id},
        )
    return reminder
