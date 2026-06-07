"""Reminder action callbacks: complete, snooze, postpone."""

from datetime import UTC, datetime, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import format_scheduled_at
from app.db.models.audit_event import AuditActorType, AuditSource
from app.db.models.task import TaskStatus
from app.services.task import (
    change_status,
    create_reminder,
    get_task,
    reschedule_task,
)
from app.todobot.states.task import TaskPostpone
from app.todobot.utils.nlp import parse_datetime_text
from app.workers.scheduling import schedule_reminder, supersede_unsent_reminders

router = Router()


@router.callback_query(F.data.startswith("raction:"))
async def handle_reminder_action(
    callback: CallbackQuery,
    state: FSMContext,
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
        task = await change_status(
            db,
            task_id=task.id,
            new_status=TaskStatus.COMPLETED,
            actor_type=AuditActorType.TELEGRAM,
            actor_id=callback.from_user.id if callback.from_user else None,
            source=AuditSource.TODOBOT,
        )
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
        await state.set_state(TaskPostpone.waiting_for_datetime)
        await state.update_data(postpone_task_id=task_id)
        await callback.message.answer(
            "When should I postpone it to? Send a new date/time.",
        )
        return


@router.message(TaskPostpone.waiting_for_datetime)
async def handle_postpone_datetime(
    message: Message,
    state: FSMContext,
    db: AsyncSession,
) -> None:
    if not message.text:
        await message.answer("Please send a date and time, e.g. tomorrow 3pm.")
        return

    parsed = parse_datetime_text(message.text)
    if not parsed:
        await message.answer("Couldn't parse that. Try e.g. tomorrow 3pm.")
        return

    data = await state.get_data()
    task_id = data.get("postpone_task_id")
    if not task_id:
        await state.clear()
        await message.answer(
            "Postpone session expired. Use the reminder buttons again.",
        )
        return

    task = await reschedule_task(
        db,
        task_id=int(task_id),
        scheduled_at=parsed,
        actor_type=AuditActorType.TELEGRAM,
        actor_id=message.from_user.id if message.from_user else None,
        source=AuditSource.TODOBOT,
    )
    await state.clear()
    await message.answer(
        f'Postponed "{task.title}" to {format_scheduled_at(task.scheduled_at)}.',
    )
