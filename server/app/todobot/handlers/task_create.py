"""AI intake and guided task creation flows."""

from contextlib import suppress
from datetime import datetime, time

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.core.utils import format_display_date, local_naive_to_utc, local_now
from app.db.documents.task import IntakeStatus
from app.db.registry import DatabaseRegistry
from app.schemas.task_intake import ClarificationQuestion, TaskDraft
from app.services.task import STATIC_REMINDER_LABEL, create_with_sync
from app.services.task_intake import TaskIntakeService
from app.todobot.keyboards.menu import main_menu
from app.todobot.keyboards.task import (
    clarify_cancel,
    confirmation,
    date_picker,
    field_edit_menu,
    skip_button,
    time_picker,
    with_flow_nav,
)
from app.todobot.states.task import TaskCreation
from app.todobot.utils.calendar_status import calendar_post_create_line
from app.todobot.utils.markdown import escape_md
from app.todobot.utils.nlp import parse_task_input

router = Router()

AI_PROMPT = (
    "Send your task in one message.\n\n"
    'Example: "Tomorrow at 18:00 gym near city center"'
)
GUIDED_PROMPT = "What task?"

_FIELD_ORDER = ("title", "date", "time", "location", "notes")


async def _track_msg(state: FSMContext, msg_id: int) -> None:
    data = await state.get_data()
    ids = data.get("_msg_ids", [])
    ids.append(msg_id)
    await state.update_data(_msg_ids=ids)


async def _cleanup_messages(bot: Bot, chat_id: int, state: FSMContext) -> None:
    data = await state.get_data()
    for msg_id in data.get("_msg_ids", []):
        with suppress(Exception):
            await bot.delete_message(chat_id, msg_id)


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


def _format_summary(data: dict[str, object]) -> str:
    lines = [f"*Task:* {escape_md(str(data.get('title') or '—'))}"]
    date_val = data.get("date")
    if date_val:
        lines.append(f"*Date:* {format_display_date(str(date_val))}")
    if data.get("time"):
        lines.append(f"*Time:* {data['time']}")
    if data.get("location"):
        lines.append(f"*Location:* {escape_md(str(data['location']))}")
    if data.get("notes"):
        lines.append(f"*Notes:* {escape_md(str(data['notes']))}")
    lines.append(f"*{STATIC_REMINDER_LABEL}*")
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
    from app.todobot.keyboards.task import flow_nav

    await state.clear()
    await _track_msg(state, message.message_id)
    await state.set_state(TaskCreation.waiting_for_title)
    sent = await message.answer(GUIDED_PROMPT, reply_markup=flow_nav())
    await _track_msg(state, sent.message_id)


async def _start_ai_intake(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _track_msg(state, message.message_id)
    await state.set_state(TaskCreation.waiting_for_input)
    sent = await message.answer(AI_PROMPT, reply_markup=clarify_cancel())
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


async def _ask_clarification(
    message: Message,
    state: FSMContext,
    question: ClarificationQuestion,
    *,
    draft: TaskDraft | None = None,
) -> None:
    await state.set_state(TaskCreation.clarifying)
    await state.update_data(clarify_field=question.field)
    if question.field == "scheduled_date":
        sent = await message.answer(
            question.question,
            reply_markup=with_flow_nav(date_picker()),
        )
    elif question.field == "scheduled_time":
        selected = draft.scheduled_date if draft else None
        sent = await message.answer(
            question.question,
            reply_markup=with_flow_nav(time_picker(selected)),
        )
    else:
        sent = await message.answer(question.question, reply_markup=clarify_cancel())
    await _track_msg(state, sent.message_id)


async def _process_intake_message(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
    text: str,
) -> None:
    if not message.from_user:
        return

    working = await message.answer("Working…")
    await _track_msg(state, working.message_id)

    svc = TaskIntakeService(registry)
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
        with suppress(Exception):
            await working.edit_text(
                "I couldn't parse that right now. Try /new guided for step-by-step.",
            )
        await state.clear()
        return

    question = svc.next_clarification_question(result)
    if question:
        with suppress(Exception):
            await working.edit_text("Got it — one quick question.")
        await _ask_clarification(
            message,
            state,
            question,
            draft=result.draft,
        )
        return

    with suppress(Exception):
        await working.edit_text("Parsed. Almost done…")
    await _prompt_reminder_or_confirm(message, state, svc, intake.id)


async def _prompt_reminder_or_confirm(
    target: Message,
    state: FSMContext,
    svc: TaskIntakeService,
    intake_id: int,
) -> None:
    """Load intake draft into FSM and show confirmation (static reminders)."""
    intake = await svc.get_intake(intake_id)
    draft = svc.draft_from_intake(intake)
    await state.update_data(intake_id=intake_id, **_draft_to_fsm_data(draft))
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
    registry: DatabaseRegistry,
) -> None:
    if not message.text:
        await message.answer("Please send a text message.")
        return

    await _track_msg(state, message.message_id)
    await _process_intake_message(message, state, registry, message.text.strip())


@router.message(TaskCreation.clarifying)
async def handle_clarification(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
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

    svc = TaskIntakeService(registry)
    try:
        result = await svc.apply_clarification(int(intake_id), message.text.strip())
    except Exception:
        sent = await message.answer(
            "I couldn't update that. Please try again.",
            reply_markup=clarify_cancel(),
        )
        await _track_msg(state, sent.message_id)
        return

    intake = await svc.get_intake(int(intake_id))
    if intake.status == IntakeStatus.CANCELLED:
        await state.clear()
        await message.answer(
            "I couldn't nail that down. Try *Guided task* for step-by-step.",
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )
        return

    question = svc.next_clarification_question(result)
    if question:
        await _ask_clarification(message, state, question, draft=result.draft)
        return

    await _prompt_reminder_or_confirm(message, state, svc, int(intake_id))


@router.message(TaskCreation.waiting_for_title)
async def handle_title(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not message.text:
        await message.answer("Please send a text message.")
        return

    await _track_msg(state, message.message_id)
    data = _extract_parsed_fields(message.text)
    if not data.get("title"):
        data["title"] = message.text.strip()

    await state.update_data(**data)
    await _advance_to_next_missing(message, state, registry=registry)


@router.callback_query(
    F.data.startswith("date:"),
    StateFilter(
        TaskCreation.waiting_for_date,
        TaskCreation.waiting_for_title,
        TaskCreation.waiting_for_time,
        TaskCreation.waiting_for_location,
        TaskCreation.waiting_for_notes,
        TaskCreation.clarifying,
        TaskCreation.confirming,
    ),
)
async def handle_date_callback(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message:
        return
    value = callback.data.split(":", 1)[1]
    await callback.answer()

    current = await state.get_state()
    data = await state.get_data()

    if value == "custom":
        await state.set_state(TaskCreation.waiting_for_date)
        from app.todobot.keyboards.task import flow_nav

        sent = await callback.message.answer(
            "Send the date (e.g., June 2, 15.06.2026, next Friday):",
            reply_markup=flow_nav(),
        )
        await _track_msg(state, sent.message_id)
        return

    await state.update_data(date=value)
    if current == TaskCreation.clarifying.state and data.get("intake_id"):
        svc = TaskIntakeService(registry)
        result = await svc.apply_clarification(int(data["intake_id"]), value)
        intake = await svc.get_intake(int(data["intake_id"]))
        if intake.status == IntakeStatus.CANCELLED:
            await state.clear()
            await callback.message.answer(
                "I couldn't nail that down. Try *Guided task*.",
                parse_mode="Markdown",
                reply_markup=main_menu(),
            )
            return
        question = svc.next_clarification_question(result)
        if question:
            await _ask_clarification(
                callback.message,
                state,
                question,
                draft=result.draft,
            )
            return
        await _prompt_reminder_or_confirm(
            callback.message,
            state,
            svc,
            int(data["intake_id"]),
        )
        return
    await _advance_to_next_missing(callback.message, state, registry=registry)


@router.message(TaskCreation.waiting_for_date)
async def handle_date_text(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not message.text:
        await message.answer("Please send a date.")
        return

    await _track_msg(state, message.message_id)
    parsed = parse_task_input(message.text)
    if not parsed.date:
        sent = await message.answer("I couldn't understand that date. Try again:")
        await _track_msg(state, sent.message_id)
        return

    if parsed.date < local_now().date():
        sent = await message.answer("That date is in the past. Pick a future date:")
        await _track_msg(state, sent.message_id)
        return

    await state.update_data(date=parsed.date.isoformat())
    await _advance_to_next_missing(message, state, registry=registry)


@router.callback_query(
    F.data.startswith("time:"),
    StateFilter(
        TaskCreation.waiting_for_time,
        TaskCreation.waiting_for_date,
        TaskCreation.waiting_for_title,
        TaskCreation.waiting_for_location,
        TaskCreation.waiting_for_notes,
        TaskCreation.clarifying,
        TaskCreation.confirming,
    ),
)
async def handle_time_callback(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message:
        return
    value = callback.data.split(":", 1)[1]
    await callback.answer()

    data = await state.get_data()
    current = await state.get_state()

    if value == "custom":
        await state.set_state(TaskCreation.waiting_for_time)
        from app.todobot.keyboards.task import flow_nav

        sent = await callback.message.answer(
            "Send the time (e.g., 14:30, 3pm):",
            reply_markup=flow_nav(),
        )
        await _track_msg(state, sent.message_id)
        return

    # Block past slots server-side when date is today.
    selected_date = data.get("date")
    now = local_now()
    if selected_date == now.date().isoformat():
        try:
            hour, minute = map(int, value.split(":"))
            if time(hour, minute) <= now.time():
                await callback.message.answer("That time is in the past. Pick another.")
                return
        except ValueError:
            pass

    await state.update_data(time=value)
    if current == TaskCreation.clarifying.state and data.get("intake_id"):
        svc = TaskIntakeService(registry)
        result = await svc.apply_clarification(int(data["intake_id"]), value)
        intake = await svc.get_intake(int(data["intake_id"]))
        if intake.status == IntakeStatus.CANCELLED:
            await state.clear()
            await callback.message.answer(
                "I couldn't nail that down. Try *Guided task*.",
                parse_mode="Markdown",
                reply_markup=main_menu(),
            )
            return
        question = svc.next_clarification_question(result)
        if question:
            await _ask_clarification(
                callback.message,
                state,
                question,
                draft=result.draft,
            )
            return
        await _prompt_reminder_or_confirm(
            callback.message,
            state,
            svc,
            int(data["intake_id"]),
        )
        return

    await _advance_to_next_missing(callback.message, state, registry=registry)


@router.message(TaskCreation.waiting_for_time)
async def handle_time_text(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
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

    await _advance_to_next_missing(message, state, registry=registry)


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


@router.callback_query(F.data == "skip:notes")
async def skip_notes(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return
    await callback.answer()
    await _advance_to_next_missing(callback.message, state, skip="notes")


@router.message(TaskCreation.waiting_for_notes)
async def handle_notes(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Please send notes or skip.")
        return
    await _track_msg(state, message.message_id)
    await state.update_data(notes=message.text.strip())
    await _advance_to_next_missing(message, state)


@router.callback_query(F.data == "confirm:yes")
async def confirm_task(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.message or not callback.from_user:
        return
    await callback.answer()
    data = await state.get_data()
    intake_id = data.get("intake_id")

    if intake_id:
        svc = TaskIntakeService(registry)
        try:
            task = await svc.confirm_intake(
                int(intake_id),
                telegram_user_id=callback.from_user.id,
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
        cal_line = await calendar_post_create_line(
            registry,
            telegram_user_id=callback.from_user.id,
            task=task,
        )
        await callback.message.answer(
            f'✅ Task saved! I\'ll remind you about "{escape_md(task.title)}".\n'
            f"{STATIC_REMINDER_LABEL}.\n"
            f"{cal_line}",
            reply_markup=main_menu(),
        )
        return

    task_date = str(data.get("date") or local_now().date().isoformat())
    task_time = str(data.get("time") or "12:00")
    scheduled_at = local_naive_to_utc(
        datetime.fromisoformat(f"{task_date}T{task_time}:00"),
    )

    task = await create_with_sync(
        registry,
        telegram_user_id=callback.from_user.id,
        title=str(data.get("title") or "Untitled"),
        scheduled_at=scheduled_at,
        description=data.get("notes") if isinstance(data.get("notes"), str) else None,
        location=(
            data.get("location") if isinstance(data.get("location"), str) else None
        ),
    )

    if callback.bot:
        await _cleanup_messages(callback.bot, callback.message.chat.id, state)

    await state.clear()
    cal_line = await calendar_post_create_line(
        registry,
        telegram_user_id=callback.from_user.id,
        task=task,
    )
    await callback.message.answer(
        f'✅ Task saved! I\'ll remind you about "{escape_md(task.title)}".\n'
        f"{STATIC_REMINDER_LABEL}.\n"
        f"{cal_line}",
        reply_markup=main_menu(),
    )


@router.callback_query(F.data == "confirm:edit")
async def edit_task(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return
    await callback.answer()
    await state.set_state(TaskCreation.confirming)
    sent = await callback.message.answer(
        "What do you want to change?",
        reply_markup=field_edit_menu(),
    )
    await _track_msg(state, sent.message_id)


@router.callback_query(F.data.startswith("editf:"))
async def handle_field_edit(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message:
        return
    field = callback.data.split(":", 1)[1]
    await callback.answer()
    data = await state.get_data()

    if field == "back":
        intake_id = data.get("intake_id")
        if intake_id:
            svc = TaskIntakeService(registry)
            await _show_intake_confirmation(
                callback.message,
                state,
                svc,
                int(intake_id),
            )
            return
        summary = _format_summary(data)
        await state.set_state(TaskCreation.confirming)
        sent = await callback.message.answer(
            f"{summary}\n\nConfirm this task?",
            reply_markup=confirmation(),
            parse_mode="Markdown",
        )
        await _track_msg(state, sent.message_id)
        return

    await state.update_data(_return_confirm=True)
    if field == "title":
        await state.set_state(TaskCreation.waiting_for_title)
        from app.todobot.keyboards.task import flow_nav

        sent = await callback.message.answer("New title?", reply_markup=flow_nav())
        await _track_msg(state, sent.message_id)
        return
    if field == "date":
        await state.set_state(TaskCreation.waiting_for_date)
        sent = await callback.message.answer(
            "Which day?",
            reply_markup=with_flow_nav(date_picker()),
        )
        await _track_msg(state, sent.message_id)
        return
    if field == "time":
        await state.set_state(TaskCreation.waiting_for_time)
        sent = await callback.message.answer(
            "What time?",
            reply_markup=with_flow_nav(time_picker(data.get("date"))),
        )
        await _track_msg(state, sent.message_id)


@router.callback_query(F.data == "confirm:cancel")
@router.callback_query(
    F.data == "flow:cancel",
    StateFilter(TaskCreation),
)
async def cancel_task(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.message:
        return
    await callback.answer()

    data = await state.get_data()
    intake_id = data.get("intake_id")
    if intake_id:
        with suppress(Exception):
            await TaskIntakeService(registry).cancel_intake(int(intake_id))

    if callback.bot:
        await _cleanup_messages(callback.bot, callback.message.chat.id, state)

    await state.clear()
    await callback.message.answer("Task cancelled.", reply_markup=main_menu())


@router.callback_query(F.data == "flow:back", StateFilter(TaskCreation))
async def flow_back(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return
    await callback.answer()
    data = await state.get_data()
    current = await state.get_state()

    # Clear current field and step back one in guided order.
    field_for_state = {
        TaskCreation.waiting_for_title.state: "title",
        TaskCreation.waiting_for_date.state: "date",
        TaskCreation.waiting_for_time.state: "time",
        TaskCreation.waiting_for_location.state: "location",
        TaskCreation.waiting_for_notes.state: "notes",
    }
    current_field = field_for_state.get(current or "")
    if current_field:
        await state.update_data(**{current_field: None})
        skipped = set(data.get("_skipped", []))
        skipped.discard(current_field)
        await state.update_data(_skipped=list(skipped))

    if current_field == "title" or current_field is None:
        from app.todobot.keyboards.task import flow_nav

        await state.set_state(TaskCreation.waiting_for_title)
        sent = await callback.message.answer(GUIDED_PROMPT, reply_markup=flow_nav())
        await _track_msg(state, sent.message_id)
        return

    idx = _FIELD_ORDER.index(current_field) if current_field in _FIELD_ORDER else 0
    prev = _FIELD_ORDER[max(0, idx - 1)]
    await state.update_data(**{prev: None})
    await _advance_to_next_missing(callback.message, state)


async def _return_to_confirm_if_editing(
    target: Message,
    state: FSMContext,
    registry: DatabaseRegistry | None = None,
) -> bool:
    data = await state.get_data()
    if not data.get("_return_confirm"):
        return False
    await state.update_data(_return_confirm=False)
    intake_id = data.get("intake_id")
    if intake_id and registry is not None:
        svc = TaskIntakeService(registry)
        title = data.get("title") if isinstance(data.get("title"), str) else None
        date_v = data.get("date") if isinstance(data.get("date"), str) else None
        time_v = data.get("time") if isinstance(data.get("time"), str) else None
        loc = data.get("location") if isinstance(data.get("location"), str) else None
        notes = data.get("notes") if isinstance(data.get("notes"), str) else None
        draft = TaskDraft(
            title=title,
            scheduled_date=date_v,
            scheduled_time=time_v,
            location=loc,
            description=notes,
        )
        intake = await svc.get_intake(int(intake_id))
        intake.draft_json = draft.model_dump()
        if registry.tasks is not None:
            await registry.tasks.update_intake(intake)
        await _show_intake_confirmation(target, state, svc, int(intake_id))
        return True
    summary = _format_summary(data)
    await state.set_state(TaskCreation.confirming)
    sent = await target.answer(
        f"{summary}\n\nConfirm this task?",
        reply_markup=confirmation(),
        parse_mode="Markdown",
    )
    await _track_msg(state, sent.message_id)
    return True


async def _advance_to_next_missing(
    target: Message,
    state: FSMContext,
    *,
    skip: str | None = None,
    registry: DatabaseRegistry | None = None,
) -> None:
    if await _return_to_confirm_if_editing(target, state, registry):
        return

    full_data = await state.get_data()

    if skip:
        skipped = set(full_data.get("_skipped", []))
        skipped.add(skip)
        await state.update_data(_skipped=list(skipped))
        full_data["_skipped"] = list(skipped)

    skipped_fields = set(full_data.get("_skipped", []))

    fields_order = [
        ("title", TaskCreation.waiting_for_title, "What task?", None),
        ("date", TaskCreation.waiting_for_date, "When?", with_flow_nav(date_picker())),
        (
            "time",
            TaskCreation.waiting_for_time,
            "What time?",
            with_flow_nav(time_picker(full_data.get("date"))),
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
            if field_name == "title":
                from app.todobot.keyboards.task import flow_nav

                keyboard = flow_nav()
            sent = await target.answer(prompt, reply_markup=keyboard)
            await _track_msg(state, sent.message_id)
            return

    summary = _format_summary(full_data)
    await state.set_state(TaskCreation.confirming)
    sent = await target.answer(
        f"{summary}\n\nConfirm this task?",
        reply_markup=confirmation(),
        parse_mode="Markdown",
    )
    await _track_msg(state, sent.message_id)
