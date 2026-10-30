"""Start, help, and main-menu button handlers."""

from contextlib import suppress
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.core.utils import as_utc, local_now
from app.db.documents.task import Task
from app.db.registry import DatabaseRegistry
from app.services.task import get_pending_tasks
from app.settings import get_settings
from app.todobot.keyboards.menu import (
    LABEL_CALENDAR,
    LABEL_GUIDED_TASK,
    LABEL_HELP,
    LABEL_MY_TASKS,
    LABEL_QUICK_TASK,
    LABEL_RESTART,
    main_menu,
    welcome_inline,
)
from app.todobot.utils.markdown import escape_md

router = Router()

_WELCOME_FETCH_LIMIT = 100
_WELCOME_MSG_KEY = "_welcome_msg_id"


def _task_counts(
    pending_tasks: list[Task],
    *,
    timezone_name: str,
) -> tuple[int, int, int]:
    """Return overdue, today, and total counts for pending tasks."""
    today = local_now().date()
    tz = ZoneInfo(timezone_name)
    overdue = 0
    today_count = 0
    for task in pending_tasks:
        if not task.scheduled_at:
            continue
        local_date = as_utc(task.scheduled_at).astimezone(tz).date()
        if local_date < today:
            overdue += 1
        elif local_date == today:
            today_count += 1
    return overdue, today_count, len(pending_tasks)


def build_welcome_text(
    *,
    calendar_connected: bool,
    has_open_tasks: bool,
    timezone_name: str,
    overdue_count: int,
    today_count: int,
    total_open: int,
) -> str:
    """Build the /start dashboard message (tasks opened via tasks)."""
    if calendar_connected:
        calendar_line = "📅 Calendar: *connected*"
    else:
        calendar_line = "📅 Calendar: *not connected*"

    lines = [
        "Hi — your to-do assistant.",
        f"_Timezone: {escape_md(timezone_name)}_",
        "",
        calendar_line,
        "",
        (
            f"*Open:* {total_open} · *Today:* {today_count} · "
            f"*Overdue:* {overdue_count}"
        ),
        "",
    ]

    if not has_open_tasks:
        lines.extend(
            [
                "*No open tasks yet.*",
                "_Tips:_ use *quick task* for one message, *guided task* step by step,",
                '_or type something like "Tomorrow 18:00 gym"._',
                "",
            ],
        )

    lines.extend(
        [
            "⚡ *quick task* — one message",
            "🧭 *guided task* — step by step",
            "📋 *tasks* — open your task list",
            "",
            "Use the buttons below to navigate.",
        ],
    )
    return "\n".join(lines)


def build_help_text(*, timezone_name: str) -> str:
    """Richer help text for /help and the Help menu button."""
    return "\n".join(
        [
            "*TodoBot help*",
            f"_Timezone: {escape_md(timezone_name)}_",
            "",
            "*Capture*",
            "• *quick task* — one message; clarify if needed; always confirm",
            "• *guided task* — title → date → time → optional details → reminder",
            '• *idle message* — e.g. "Friday 15:00 dentist" saves when complete',
            "",
            "*Manage*",
            "• *tasks* — closest open tasks; mark done, remove, or edit",
            "",
            "*Calendar*",
            "• Connect Google once; Sync now / month from the calendar hub",
            "• New tasks enqueue Calendar events when linked",
            "",
            "*Reminders*",
            "• At-start ping always; optional early remind on Quick/Guided",
            "• complete · snooze (ping only) · postpone (presets or custom)",
            "",
            "*Navigation*",
            "• quick · guided · tasks · calendar · help · restart",
            "• *restart* clears a flow and refreshes the dashboard",
        ],
    )


async def _plant_reply_keyboard(message: Message) -> None:
    """Attach main_menu without leaving a visible chat bubble."""
    if not message.bot:
        return
    plant = await message.answer("\u200b", reply_markup=main_menu())
    with suppress(Exception):
        await message.bot.delete_message(message.chat.id, plant.message_id)


async def _send_welcome(
    message: Message,
    registry: DatabaseRegistry,
    state: FSMContext | None = None,
    *,
    edit_msg_id: int | None = None,
) -> None:
    """Send or edit the welcome dashboard; plant reply keyboard when needed."""
    settings = get_settings()
    timezone_name = settings.TIMEZONE
    telegram_user_id = message.from_user.id if message.from_user else None
    calendar_connected = False
    pending: list[Task] = []
    if telegram_user_id is not None:
        if registry.credentials is not None:
            cred = await registry.credentials.get_google_for_telegram_user(
                telegram_user_id,
            )
            calendar_connected = cred is not None
        pending = await get_pending_tasks(
            registry,
            telegram_user_id=telegram_user_id,
            limit=_WELCOME_FETCH_LIMIT,
        )

    overdue, today_count, total_open = _task_counts(
        pending,
        timezone_name=timezone_name,
    )
    text = build_welcome_text(
        calendar_connected=calendar_connected,
        has_open_tasks=bool(pending),
        timezone_name=timezone_name,
        overdue_count=overdue,
        today_count=today_count,
        total_open=total_open,
    )
    inline = welcome_inline(calendar_connected=calendar_connected)

    if edit_msg_id and message.bot:
        with suppress(Exception):
            await message.bot.edit_message_text(
                text,
                chat_id=message.chat.id,
                message_id=edit_msg_id,
                parse_mode="Markdown",
                reply_markup=inline,
            )
            if state is not None:
                await state.update_data(**{_WELCOME_MSG_KEY: edit_msg_id})
            return

    sent = await message.answer(
        text,
        reply_markup=inline,
        parse_mode="Markdown",
    )
    await _plant_reply_keyboard(message)
    if state is not None:
        await state.update_data(**{_WELCOME_MSG_KEY: sent.message_id})


async def _send_help(message: Message) -> None:
    """Send the richer help message with the main reply keyboard."""
    settings = get_settings()
    await message.answer(
        build_help_text(timezone_name=settings.TIMEZONE),
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )


async def _do_restart(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    """Clear FSM, delete tracked flow messages, and refresh welcome in place."""
    data = await state.get_data()
    msg_ids = data.get("_msg_ids", [])
    edit_msg_id = data.get(_WELCOME_MSG_KEY)
    if msg_ids and message.bot:
        for msg_id in msg_ids:
            with suppress(Exception):
                await message.bot.delete_message(message.chat.id, msg_id)
    await state.clear()
    await _send_welcome(
        message,
        registry,
        state,
        edit_msg_id=edit_msg_id if isinstance(edit_msg_id, int) else None,
    )


async def _welcome_after_clear(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    data = await state.get_data()
    edit_msg_id = data.get(_WELCOME_MSG_KEY)
    await state.clear()
    await _send_welcome(
        message,
        registry,
        state,
        edit_msg_id=edit_msg_id if isinstance(edit_msg_id, int) else None,
    )


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    await _welcome_after_clear(message, state, registry)


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _send_help(message)


@router.message(F.text == LABEL_QUICK_TASK)
async def menu_quick_task(message: Message, state: FSMContext) -> None:
    await state.clear()
    from app.todobot.handlers.task_create import _start_ai_intake

    await _start_ai_intake(message, state)


@router.message(F.text == LABEL_GUIDED_TASK)
async def menu_guided_task(message: Message, state: FSMContext) -> None:
    await state.clear()
    from app.todobot.handlers.task_create import _start_guided

    await _start_guided(message, state)


@router.message(F.text == LABEL_MY_TASKS)
async def menu_my_tasks(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    await state.clear()
    from app.todobot.handlers.task_manage import cmd_tasks

    await cmd_tasks(message, registry, state)


@router.message(F.text == LABEL_CALENDAR)
async def menu_calendar(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    await state.clear()
    from app.todobot.handlers.calendar import open_calendar_entry

    await open_calendar_entry(message, registry)


@router.message(F.text == LABEL_HELP)
async def menu_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _send_help(message)


@router.message(F.text == LABEL_RESTART)
async def menu_restart(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    await _do_restart(message, state, registry)


@router.callback_query(F.data.startswith("w:"))
async def welcome_inline_actions(
    callback: CallbackQuery,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    if not callback.data or not callback.message:
        return
    parts = callback.data.split(":")
    if len(parts) < 2:
        return
    action = parts[1]
    await callback.answer()

    if action == "quick":
        await state.clear()
        from app.todobot.handlers.task_create import _start_ai_intake

        await _start_ai_intake(callback.message, state)
        return
    if action == "guided":
        await state.clear()
        from app.todobot.handlers.task_create import _start_guided

        await _start_guided(callback.message, state)
        return
    if action == "tasks":
        await state.clear()
        from app.todobot.handlers.task_manage import cmd_tasks

        await cmd_tasks(callback.message, registry, state)
        return
    if action in {"cal", "connect"}:
        await state.clear()
        from app.todobot.handlers.calendar import open_calendar_entry

        await open_calendar_entry(callback.message, registry)
        return
    if action == "help":
        await state.clear()
        await _send_help(callback.message)
        return
    if action == "restart":
        await _do_restart(callback.message, state, registry)
