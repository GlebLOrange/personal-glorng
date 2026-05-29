"""AI intake and guided task creation flows."""

from datetime import UTC, date, datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.google_sync_queue import SyncAction
from app.schemas.task_intake import TaskDraft
from app.services.task import create_reminder, create_task, enqueue_calendar_sync
from app.services.task_intake import TaskIntakeService
from app.todobot.keyboards.menu import main_menu
from app.todobot.keyboards.task import (
    confirmation,
    date_picker,
    reminder_presets,
    skip_button,
    time_picker,
)
from app.todobot.states.task import TaskCreation
from app.todobot.utils.nlp import parse_task_input
from app.workers.scheduling import schedule_reminder

router = Router()

AI_PROMPT = (
    "Send your task in one message.\n\n"
    'Example: "Tomorrow at 18:00 gym near city center"'
)
GUIDED_PROMPT = "What would you like me to remind you about?"


async def _track_msg(state: FSMContext, msg_id: int) -> None:
    data = await state.get_data()
    ids = data.get("_msg_ids", [])
    ids.append(msg_id)
    await state.update_data(_msg_ids=ids)


async def _cleanup_messages(bot, chat_id: int, state: FSMContext) -> None:
    data = await state.get_data()
    for msg_id in data.get("_msg_ids", []):
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception:
            pass


def _extract_parsed_fields(text: str) -> dict[str, str | None]:
    parsed = parse_task_input(text)
    data: dict[str, str | None] = {}
    if parsed.title:
        data["title"] = parsed.title
    if parsed.date:
        data["date"] = parsed.date.isoformat()
    if parsed.time:
        data["time"] = parsed.time.strftime("%H:%M")
    if parsed.location:
        data["location"] = parsed.location
    return data


def _format_summary(data: dict[str, str | None]) -> str:
    lines = [f"*Task:* {data.get('title', '—')}"]
    if data.get("date"):
        lines.append(f"*Date:* {data['date']}")
    if data.get("time"):
        lines.append(f"*Time:* {data['time']}")
    if data.get("location"):
        lines.append(f"*Location:* {data['location']}")
    if data.get("notes"):
        lines.append(f"*Notes:* {data['notes']}")
    return "\n".join(lines)


def _draft_to_fsm_data(draft: TaskDraft) -> dict[str, str | None]:
    return {
        "title": draft.title,
        "date": draft.scheduled_date,
        "time": draft.scheduled_time,
        "location": draft.location,
        "notes": draft.description,
    }


async def _start_guided(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _track_msg(state, message.message_id)
    await state.set_state(TaskCreation.waiting_for_title)
    sent = await message.answer(GUIDED_PROMPT)
    await _track_msg(state, sent.message_id)


async def _start_ai_intake(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _track_msg(state, message.message_id)
    await state.set_state(TaskCreation.waiting_for_input)
    sent = await message.answer(AI_PROMPT)
    await _track_msg(state, sent.message_id)


@router.message(Command("new"))
async def cmd_new_task(
    message: Message,
    state: FSMContext,
    command: CommandObject,
) -> None:
    if command.args and command.args.strip().lower() == "guided":
        await _start_guided(message, state)
    else:
        await _start_ai_intake(message, state)


async def _process_intake_message(
    message: Message,
    state: FSMContext,
    db: AsyncSession,
    text: str,
) -> None:
    if not message.from_user:
        return

    svc = TaskIntakeService(db)
    inbound = await svc.store_inbound_message(
        telegram_user_id=message.from_user.id,
        telegram_message_id=message.message_id,
        chat_id=message.chat.id,
        text=text,
        metadata={"chat_type": message.chat.type},
    )
    intake = await svc.create_intake_from_message(inbound)
    await state.update_data(intake_id=intake.id)

    try:
        result = await svc.run_extraction(intake)
    except Exception:
        sent = await message.answer(
            "I couldn't parse that right now. Try /new guided for step-by-step.",
            reply_markup=main_menu(),
        )
        await _track_msg(state, sent.message_id)
        await state.clear()
        return

    question = svc.next_clarification_question(result)
    if question:
        await state.set_state(TaskCreation.clarifying)
        sent = await message.answer(question.question)
        await _track_msg(state, sent.message_id)
        return

    await _prompt_reminder_or_confirm(message, state, svc, intake.id)


async def _prompt_reminder_or_confirm(
    target: Message,
    state: FSMContext,
    svc: TaskIntakeService,
    intake_id: int,
) -> None:
    intake = await svc.get_intake(intake_id)
    draft = svc.draft_from_intake(intake)
    await state.update_data(intake_id=intake_id, **_draft_to_fsm_data(draft))

    if draft.reminder_minutes is None:
        await state.set_state(TaskCreation.waiting_for_reminder)
        sent = await target.answer(
            "How early should I remind you?",
            reply_markup=reminder_presets(),
        )
        await _track_msg(state, sent.message_id)
        return

    await state.update_data(reminder_minutes=draft.reminder_minutes)
    await _show_intake_confirmation(target, state, svc, intake_id)


async def _show_intake_confirmation(
    target: Message,
    state: FSMContext,
    svc: TaskIntakeService,
    intake_id: int,
) -> None:
    intake = await svc.get_intake(intake_id)
    draft = svc.draft_from_intake(intake)
    summary = svc.build_confirmation_summary(draft)
    await state.set_state(TaskCreation.confirming)
    sent = await target.answer(
        f"{summary}\n\nConfirm this task?",
        reply_markup=confirmation(),
        parse_mode="Markdown",
    )
    await _track_msg(state, sent.message_id)


@router.message(TaskCreation.waiting_for_input)
async def handle_natural_input(
    message: Message,
    state: FSMContext,
    db: AsyncSession,
) -> None:
    if not message.text:
        await message.answer("Please send a text message.")
        return

    await _track_msg(state, message.message_id)
    await _process_intake_message(message, state, db, message.text.strip())


@router.message(TaskCreation.clarifying)
async def handle_clarification(
    message: Message,
    state: FSMContext,
    db: AsyncSession,
) -> None:
    if not message.text:
        await message.answer("Please send a text reply.")
        return

    await _track_msg(state, message.message_id)
    data = await state.get_data()
    intake_id = data.get("intake_id")
    if not intake_id:
        await message.answer("Session expired. Use /new to start again.")
        await state.clear()
        return

    svc = TaskIntakeService(db)
    try:
        result = await svc.apply_clarification(int(intake_id), message.text.strip())
    except Exception:
        sent = await message.answer("I couldn't update that. Please try again.")
        await _track_msg(state, sent.message_id)
        return

    question = svc.next_clarification_question(result)
    if question:
        await state.set_state(TaskCreation.clarifying)
        sent = await message.answer(question.question)
        await _track_msg(state, sent.message_id)
        return

    await _prompt_reminder_or_confirm(message, state, svc, int(intake_id))


@router.message(TaskCreation.waiting_for_title)
async def handle_title(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Please send a text message.")
        return

    await _track_msg(state, message.message_id)
    data = _extract_parsed_fields(message.text)
    if not data.get("title"):
        data["title"] = message.text.strip()

    await state.update_data(**data)
    await _advance_to_next_missing(message, state)


@router.callback_query(F.data.startswith("date:"))
async def handle_date_callback(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.data or not callback.message:
        return
    value = callback.data.split(":", 1)[1]
    await callback.answer()

    if value == "custom":
        await state.set_state(TaskCreation.waiting_for_date)
        sent = await callback.message.answer(
            "Send the date (e.g., June 2, 2026-06-15, next Friday):",
        )
        await _track_msg(state, sent.message_id)
        return

    await state.update_data(date=value)
    await _advance_to_next_missing(callback.message, state)


@router.message(TaskCreation.waiting_for_date)
async def handle_date_text(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Please send a date.")
        return

    await _track_msg(state, message.message_id)
    parsed = parse_task_input(message.text)
    if not parsed.date:
        sent = await message.answer("I couldn't understand that date. Try again:")
        await _track_msg(state, sent.message_id)
        return

    if parsed.date < date.today():
        sent = await message.answer("That date is in the past. Pick a future date:")
        await _track_msg(state, sent.message_id)
        return

    await state.update_data(date=parsed.date.isoformat())
    await _advance_to_next_missing(message, state)


@router.callback_query(F.data.startswith("time:"))
async def handle_time_callback(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.data or not callback.message:
        return
    value = callback.data.split(":", 1)[1]
    await callback.answer()

    if value == "custom":
        await state.set_state(TaskCreation.waiting_for_time)
        sent = await callback.message.answer("Send the time (e.g., 14:30, 3pm):")
        await _track_msg(state, sent.message_id)
        return

    await state.update_data(time=value)
    await _advance_to_next_missing(callback.message, state)


@router.message(TaskCreation.waiting_for_time)
async def handle_time_text(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Please send a time.")
        return

    await _track_msg(state, message.message_id)
    parsed = parse_task_input(message.text)
    if parsed.time:
        await state.update_data(time=parsed.time.strftime("%H:%M"))
    else:
        try:
            t = datetime.strptime(message.text.strip(), "%H:%M")
            await state.update_data(time=t.strftime("%H:%M"))
        except ValueError:
            sent = await message.answer(
                "I couldn't understand that time. Try HH:MM format:",
            )
            await _track_msg(state, sent.message_id)
            return

    await _advance_to_next_missing(message, state)


@router.message(TaskCreation.waiting_for_location)
async def handle_location(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Please send a location or skip.")
        return
    await _track_msg(state, message.message_id)
    await state.update_data(location=message.text.strip())
    await _advance_to_next_missing(message, state)


@router.callback_query(F.data == "skip:location")
async def skip_location(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return
    await callback.answer()
    await _advance_to_next_missing(callback.message, state, skip="location")


@router.message(TaskCreation.waiting_for_notes)
async def handle_notes(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Please send notes or skip.")
        return
    await _track_msg(state, message.message_id)
    await state.update_data(notes=message.text.strip())
    await _advance_to_next_missing(message, state)


@router.callback_query(F.data == "skip:notes")
async def skip_notes(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return
    await callback.answer()
    await _advance_to_next_missing(callback.message, state, skip="notes")


@router.callback_query(F.data.startswith("remind:"))
async def handle_reminder_choice(
    callback: CallbackQuery,
    state: FSMContext,
    db: AsyncSession,
) -> None:
    if not callback.data or not callback.message:
        return
    value = callback.data.split(":", 1)[1]
    await callback.answer()

    if value == "none":
        await state.update_data(reminder_minutes=None)
    else:
        await state.update_data(reminder_minutes=int(value))

    data = await state.get_data()
    intake_id = data.get("intake_id")
    if intake_id:
        svc = TaskIntakeService(db)
        await _show_intake_confirmation(callback.message, state, svc, int(intake_id))
        return

    await state.set_state(TaskCreation.confirming)
    summary = _format_summary(data)
    sent = await callback.message.answer(
        f"{summary}\n\nConfirm this task?",
        reply_markup=confirmation(),
        parse_mode="Markdown",
    )
    await _track_msg(state, sent.message_id)


@router.callback_query(F.data == "confirm:yes")
async def confirm_task(
    callback: CallbackQuery,
    state: FSMContext,
    db: AsyncSession,
) -> None:
    if not callback.message or not callback.from_user:
        return
    await callback.answer()
    data = await state.get_data()
    intake_id = data.get("intake_id")

    if intake_id:
        svc = TaskIntakeService(db)
        reminder_minutes = data.get("reminder_minutes")
        try:
            task = await svc.confirm_intake(
                int(intake_id),
                telegram_user_id=callback.from_user.id,
                reminder_minutes=reminder_minutes,
            )
        except Exception:
            await callback.message.answer(
                "Could not save the task. Try /new again.",
                reply_markup=main_menu(),
            )
            await state.clear()
            return

        if callback.bot:
            await _cleanup_messages(
                callback.bot,
                callback.message.chat.id,
                state,
            )
        await state.clear()
        await callback.message.answer(
            f'✅ Task saved! I\'ll remind you about "{task.title}".',
            reply_markup=main_menu(),
        )
        return

    task_date = data.get("date", date.today().isoformat())
    task_time = data.get("time", "12:00")
    scheduled_str = f"{task_date}T{task_time}:00"

    task = await create_task(
        db,
        telegram_user_id=callback.from_user.id,
        title=data.get("title", "Untitled"),
        scheduled_at=scheduled_str,
        description=data.get("notes"),
        location=data.get("location"),
    )

    reminder_minutes = data.get("reminder_minutes")
    if reminder_minutes:
        scheduled_dt = datetime.fromisoformat(scheduled_str).replace(tzinfo=UTC)
        remind_at = scheduled_dt - timedelta(minutes=int(reminder_minutes))
        if remind_at > datetime.now(UTC):
            reminder = await create_reminder(db, task_id=task.id, remind_at=remind_at)
            await schedule_reminder(db, reminder)

    await enqueue_calendar_sync(db, task_id=task.id, action=SyncAction.CREATE)

    if callback.bot:
        await _cleanup_messages(callback.bot, callback.message.chat.id, state)

    await state.clear()
    await callback.message.answer(
        f'✅ Task saved! I\'ll remind you about "{task.title}".',
        reply_markup=main_menu(),
    )


@router.callback_query(F.data == "confirm:edit")
async def edit_task(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return
    await callback.answer()

    data = await state.get_data()
    if data.get("intake_id"):
        await _start_ai_intake(callback.message, state)
        return

    if callback.bot:
        await _cleanup_messages(callback.bot, callback.message.chat.id, state)

    await state.clear()
    await state.set_state(TaskCreation.waiting_for_title)
    sent = await callback.message.answer(
        "Let's start over. What would you like me to remind you about?",
    )
    await _track_msg(state, sent.message_id)


@router.callback_query(F.data == "confirm:cancel")
async def cancel_task(
    callback: CallbackQuery,
    state: FSMContext,
    db: AsyncSession,
) -> None:
    if not callback.message:
        return
    await callback.answer()

    data = await state.get_data()
    intake_id = data.get("intake_id")
    if intake_id:
        await TaskIntakeService(db).cancel_intake(int(intake_id))

    if callback.bot:
        await _cleanup_messages(callback.bot, callback.message.chat.id, state)

    await state.clear()
    await callback.message.answer("Task cancelled.", reply_markup=main_menu())


async def _advance_to_next_missing(
    target: Message,
    state: FSMContext,
    *,
    skip: str | None = None,
) -> None:
    full_data = await state.get_data()

    if skip:
        skipped = set(full_data.get("_skipped", []))
        skipped.add(skip)
        await state.update_data(_skipped=list(skipped))
        full_data["_skipped"] = list(skipped)

    skipped_fields = set(full_data.get("_skipped", []))

    fields_order = [
        ("title", TaskCreation.waiting_for_title, "What task?", None),
        ("date", TaskCreation.waiting_for_date, "When?", date_picker()),
        (
            "time",
            TaskCreation.waiting_for_time,
            "What time?",
            time_picker(full_data.get("date")),
        ),
        (
            "location",
            TaskCreation.waiting_for_location,
            "Where? (or skip)",
            skip_button("location"),
        ),
        (
            "notes",
            TaskCreation.waiting_for_notes,
            "Additional notes? (or skip)",
            skip_button("notes"),
        ),
    ]

    for field_name, field_state, prompt, keyboard in fields_order:
        if field_name in skipped_fields:
            continue
        if not full_data.get(field_name):
            await state.set_state(field_state)
            sent = await target.answer(prompt, reply_markup=keyboard)
            await _track_msg(state, sent.message_id)
            return

    await state.set_state(TaskCreation.waiting_for_reminder)
    sent = await target.answer(
        "How early should I remind you?",
        reply_markup=reminder_presets(),
    )
    await _track_msg(state, sent.message_id)
