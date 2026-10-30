"""Reminder action callbacks: complete, snooze, postpone."""

from contextlib import suppress
from datetime import UTC, datetime, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.core.utils import format_scheduled_at, local_naive_to_utc, local_now
from app.db.documents.audit import AuditActorType, AuditSource
from app.db.documents.task import Task, TaskStatus
from app.db.registry import DatabaseRegistry
from app.services.task import (
    change_status,
    create_reminder,
    get_task,
    reschedule_task,
)
from app.todobot.keyboards.task import postpone_presets
from app.todobot.states.task import TaskPostpone
from app.todobot.utils.markdown import escape_md
from app.todobot.utils.nlp import parse_datetime_text
from app.workers.scheduling import schedule_reminder, supersede_unsent_reminders

router = Router()


async def _strip_keyboard(callback: CallbackQuery) -> None:
    if callback.message:
        with suppress(Exception):
            await callback.message.edit_reply_markup(reply_markup=None)


async def _owned_reminder_task(
    registry: DatabaseRegistry,
    *,
    task_id: int,
    telegram_user_id: int,
) -> Task | None:
    task = await get_task(registry, task_id=task_id)
    if not task or task.telegram_user_id != telegram_user_id:
        return None
    return task


async def _recreate_at_start_reminder(
    registry: DatabaseRegistry,
    *,
    task_id: int,
    scheduled_at: datetime,
) -> None:
    await supersede_unsent_reminders(registry, task_id)
    reminder = await create_reminder(registry, task_id=task_id, remind_at=scheduled_at)
    await schedule_reminder(registry, reminder)


@router.callback_query(F.data.startswith("raction:"))
async def handle_reminder_action(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message or not callback.from_user:
        return

    parts = callback.data.split(":")
    if len(parts) < 3:
        return

    task_id = int(parts[1])
    action = parts[2]

    await callback.answer()

    task = await _owned_reminder_task(
        registry,
        task_id=task_id,
        telegram_user_id=callback.from_user.id,
    )
    if not task:
        await callback.message.answer("Task not found.")
        return

    if action == "complete":
        task = await change_status(
            registry,
            task_id=task.id,
            new_status=TaskStatus.COMPLETED,
            actor_type=AuditActorType.TELEGRAM,
            actor_id=callback.from_user.id,
            source=AuditSource.TODOBOT,
            allow_future_complete=True,
        )
        await _strip_keyboard(callback)
        await callback.message.answer(
            f'Task "{escape_md(task.title)}" completed!',
        )
        return

    if action == "snooze" and len(parts) == 4:
        # Keep ping-only snooze (does not shift scheduled_at).
        minutes = int(parts[3])
        remind_at = datetime.now(UTC) + timedelta(minutes=minutes)
        await supersede_unsent_reminders(registry, task.id)
        reminder = await create_reminder(registry, task_id=task.id, remind_at=remind_at)
        await schedule_reminder(registry, reminder)
        await _strip_keyboard(callback)
        await callback.message.answer(
            f'Snoozed! I\'ll remind you about "{escape_md(task.title)}" '
            f"in {minutes} minutes.",
        )
        return

    if action == "postpone":
        await state.set_state(TaskPostpone.waiting_for_datetime)
        await state.update_data(postpone_task_id=task_id)
        await callback.message.answer(
            "When should I postpone it to?",
            reply_markup=postpone_presets(),
        )
        return


@router.callback_query(F.data.startswith("pp:"))
async def handle_postpone_preset(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message or not callback.from_user:
        return
    choice = callback.data.split(":", 1)[1]
    await callback.answer()

    data = await state.get_data()
    task_id = data.get("postpone_task_id")
    if not task_id:
        await callback.message.answer(
            "Postpone session expired. Use the reminder buttons again.",
        )
        return

    task = await _owned_reminder_task(
        registry,
        task_id=int(task_id),
        telegram_user_id=callback.from_user.id,
    )
    if not task:
        await state.clear()
        await callback.message.answer("Task not found.")
        return

    if choice == "custom":
        await callback.message.answer("Send a new date/time (e.g. tomorrow 3pm).")
        return

    now = local_now()
    if choice == "1h":
        new_at = local_naive_to_utc(now.replace(tzinfo=None) + timedelta(hours=1))
    elif choice == "tm09":
        tomorrow = (now + timedelta(days=1)).replace(
            hour=9,
            minute=0,
            second=0,
            microsecond=0,
        )
        new_at = local_naive_to_utc(tomorrow.replace(tzinfo=None))
    else:
        await callback.message.answer("Unknown postpone option.")
        return

    task = await reschedule_task(
        registry,
        task_id=int(task_id),
        scheduled_at=new_at,
        actor_type=AuditActorType.TELEGRAM,
        actor_id=callback.from_user.id,
        source=AuditSource.TODOBOT,
    )
    await _recreate_at_start_reminder(
        registry,
        task_id=task.id,
        scheduled_at=task.scheduled_at,
    )
    await state.clear()
    await _strip_keyboard(callback)
    when = format_scheduled_at(task.scheduled_at)
    await callback.message.answer(
        f'Postponed "{escape_md(task.title)}" to {when}.',
    )


@router.message(TaskPostpone.waiting_for_datetime)
async def handle_postpone_datetime(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not message.text or not message.from_user:
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

    task = await _owned_reminder_task(
        registry,
        task_id=int(task_id),
        telegram_user_id=message.from_user.id,
    )
    if not task:
        await state.clear()
        await message.answer("Task not found.")
        return

    task = await reschedule_task(
        registry,
        task_id=int(task_id),
        scheduled_at=parsed,
        actor_type=AuditActorType.TELEGRAM,
        actor_id=message.from_user.id,
        source=AuditSource.TODOBOT,
    )
    await _recreate_at_start_reminder(
        registry,
        task_id=task.id,
        scheduled_at=task.scheduled_at,
    )
    await state.clear()
    when = format_scheduled_at(task.scheduled_at)
    await message.answer(
        f'Postponed "{escape_md(task.title)}" to {when}.',
    )
