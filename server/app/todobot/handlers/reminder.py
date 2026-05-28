"""Reminder action callbacks: complete, snooze, postpone."""

from datetime import UTC, datetime, timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import TaskStatus
from app.services.task import create_reminder, get_task, update_task_status
from app.workers.scheduling import schedule_reminder, supersede_unsent_reminders

router = Router()


@router.callback_query(F.data.startswith("raction:"))
async def handle_reminder_action(
    callback: CallbackQuery,
    db: AsyncSession,
) -> None:
    if not callback.data or not callback.message:
        return

    parts = callback.data.split(":")
    if len(parts) < 3:
        return

    task_id = int(parts[1])
    action = parts[2]

    await callback.answer()

    task = await get_task(db, task_id=task_id)
    if not task:
        await callback.message.answer("Task not found.")
        return

    if action == "complete":
        await update_task_status(db, task=task, new_status=TaskStatus.COMPLETED)
        await callback.message.answer(
            f'Task "{task.title}" completed!',
        )
        return

    if action == "snooze" and len(parts) == 4:
        minutes = int(parts[3])
        remind_at = datetime.now(UTC) + timedelta(minutes=minutes)
        await supersede_unsent_reminders(db, task.id)
        reminder = await create_reminder(db, task_id=task.id, remind_at=remind_at)
        await schedule_reminder(db, reminder)
        await callback.message.answer(
            f'Snoozed! I\'ll remind you about "{task.title}" in {minutes} minutes.',
        )
        return

    if action == "postpone":
        await callback.message.answer(
            "When should I postpone it to? Send a new date/time.",
        )
