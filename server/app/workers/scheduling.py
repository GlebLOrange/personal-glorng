"""Enqueue and supersede reminder jobs."""

from datetime import UTC, datetime

from app.core.logging import logger
from app.core.utils import as_utc
from app.db.documents.task import Reminder
from app.db.registry import DatabaseRegistry
from app.workers.job_names import JobName
from app.workers.queue import get_job_queue


async def supersede_unsent_reminders(
    registry: DatabaseRegistry,
    task_id: int,
    *,
    exclude_id: int | None = None,
) -> None:
    """Abort and delete unsent future reminders for a task."""
    if registry.tasks is None:
        msg = "Tasks repository is not initialized"
        raise RuntimeError(msg)

    now = datetime.now(UTC)
    reminders = await registry.tasks.delete_unsent_reminders(
        task_id,
        now=now,
        exclude_id=exclude_id,
    )
    queue = get_job_queue()
    for reminder in reminders:
        if reminder.job_id:
            await queue.revoke(reminder.job_id)

    if not reminders:
        return

    logger.info(
        "Superseded unsent reminders",
        context={"task_id": task_id, "count": len(reminders)},
    )


async def schedule_reminder(
    registry: DatabaseRegistry,
    reminder: Reminder,
) -> Reminder:
    """Enqueue send_reminder for a DB reminder row."""
    if registry.tasks is None:
        msg = "Tasks repository is not initialized"
        raise RuntimeError(msg)

    now = datetime.now(UTC)
    remind_at = as_utc(reminder.remind_at)
    if reminder.sent or remind_at <= now or reminder.job_id:
        return reminder

    queue = get_job_queue()
    job_id = await queue.enqueue(
        JobName.SEND_REMINDER,
        reminder.id,
        eta=remind_at,
    )
    reminder = await registry.tasks.update_reminder(reminder.id, job_id=job_id)
    logger.info(
        "Reminder scheduled",
        context={"reminder_id": reminder.id, "job_id": job_id},
    )
    return reminder
