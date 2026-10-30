"""Idle one-shot task capture: short message → task + calendar + reminder."""

from aiogram import F, Router
from aiogram.filters import Filter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.core.utils import format_scheduled_at
from app.db.registry import DatabaseRegistry
from app.services.task import create_with_sync
from app.todobot.keyboards.menu import ALL_LABELS, main_menu
from app.todobot.keyboards.task import (
    clarify_cancel,
    date_picker,
    time_picker,
    with_flow_nav,
)
from app.todobot.states.task import OneShotCapture
from app.todobot.utils.nlp import ParsedTask, parse_task_input
from app.todobot.utils.oneshot import (
    OneshotAction,
    clarification_prompt,
    first_missing_field,
    merge_clarification,
    oneshot_action,
    parsed_from_fsm,
    parsed_to_fsm,
    scheduled_at_from_parsed,
)

router = Router()


class OneshotCandidateFilter(Filter):
    """Match idle text that looks like a dated/timed task, not chatter."""

    async def __call__(self, message: Message) -> bool | dict[str, object]:
        if not message.text:
            return False
        text = message.text.strip()
        if not text or text.startswith("/") or text in ALL_LABELS:
            return False
        parsed = parse_task_input(text)
        action = oneshot_action(parsed)
        if action == OneshotAction.IGNORE:
            return False
        return {"parsed": parsed, "oneshot_gate": action}


async def _calendar_linked(registry: DatabaseRegistry, telegram_user_id: int) -> bool:
    if registry.credentials is None:
        return False
    cred = await registry.credentials.get_google_for_telegram_user(telegram_user_id)
    return cred is not None


async def _save_oneshot(
    message: Message,
    registry: DatabaseRegistry,
    parsed: ParsedTask,
) -> None:
    if not message.from_user:
        return
    scheduled_at = scheduled_at_from_parsed(parsed)
    title = parsed.title or "Untitled"
    task = await create_with_sync(
        registry,
        telegram_user_id=message.from_user.id,
        title=title,
        scheduled_at=scheduled_at,
        description=parsed.notes,
        location=parsed.location,
        reminder_minutes=None,
    )
    linked = await _calendar_linked(registry, message.from_user.id)
    when = format_scheduled_at(task.scheduled_at)
    lines = [
        f'✅ Saved "{task.title}" for {when}.',
        "I'll message you at that time.",
    ]
    if linked:
        lines.append("📅 Also queued for Google Calendar.")
    else:
        lines.append("📅 Calendar not linked — /connect_calendar to sync events.")
    await message.answer("\n".join(lines), reply_markup=main_menu())


async def _ask_missing(
    message: Message,
    state: FSMContext,
    parsed: ParsedTask,
) -> None:
    field = first_missing_field(parsed)
    if field is None:
        return
    await state.set_state(OneShotCapture.waiting_for_missing)
    await state.update_data(missing_field=field, **parsed_to_fsm(parsed))
    prompt = clarification_prompt(parsed)
    if field == "date":
        markup = with_flow_nav(date_picker())
    elif field == "time":
        date_iso = parsed.date.isoformat() if parsed.date else None
        markup = with_flow_nav(time_picker(date_iso))
    else:
        markup = clarify_cancel()
    await message.answer(prompt, reply_markup=markup)


@router.message(StateFilter(None), OneshotCandidateFilter())
async def handle_idle_oneshot(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
    parsed: ParsedTask,
    oneshot_gate: OneshotAction,
) -> None:
    """Idle chat with day/time → save immediately or ask one question."""
    if oneshot_gate == OneshotAction.SAVE:
        await _save_oneshot(message, registry, parsed)
        return
    await _ask_missing(message, state, parsed)


@router.message(OneShotCapture.waiting_for_missing, F.text)
async def handle_oneshot_clarification(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not message.text:
        return
    data = await state.get_data()
    field = str(data.get("missing_field") or "")
    draft = parsed_from_fsm(data)
    updated = merge_clarification(draft, message.text, field)
    if updated.is_complete:
        await state.clear()
        await _save_oneshot(message, registry, updated)
        return
    await _ask_missing(message, state, updated)


@router.callback_query(F.data.startswith("date:"), OneShotCapture.waiting_for_missing)
async def oneshot_date_pick(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message:
        return
    value = callback.data.split(":", 1)[1]
    await callback.answer()
    if value == "custom":
        await callback.message.answer("Send the date:", reply_markup=clarify_cancel())
        return
    data = await state.get_data()
    draft = parsed_from_fsm(data)
    updated = merge_clarification(draft, value, "date")
    if updated.is_complete:
        await state.clear()
        await _save_oneshot(callback.message, registry, updated)
        return
    await _ask_missing(callback.message, state, updated)


@router.callback_query(F.data.startswith("time:"), OneShotCapture.waiting_for_missing)
async def oneshot_time_pick(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message:
        return
    value = callback.data.split(":", 1)[1]
    await callback.answer()
    if value == "custom":
        await callback.message.answer("Send the time:", reply_markup=clarify_cancel())
        return
    data = await state.get_data()
    draft = parsed_from_fsm(data)
    updated = merge_clarification(draft, value, "time")
    if updated.is_complete:
        await state.clear()
        await _save_oneshot(callback.message, registry, updated)
        return
    await _ask_missing(callback.message, state, updated)


@router.callback_query(F.data == "flow:cancel", OneShotCapture.waiting_for_missing)
async def oneshot_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return
    await callback.answer()
    await state.clear()
    await callback.message.answer("Cancelled.", reply_markup=main_menu())
