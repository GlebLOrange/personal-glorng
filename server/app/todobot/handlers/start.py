"""Start, help, and main-menu button handlers."""

from contextlib import suppress

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.core.utils import format_scheduled_at
from app.db.documents.task import Task
from app.db.registry import DatabaseRegistry
from app.services.task import get_pending_tasks
from app.todobot.keyboards.menu import (
    LABEL_CALENDAR,
    LABEL_GUIDED_TASK,
    LABEL_HELP,
    LABEL_MY_TASKS,
    LABEL_QUICK_TASK,
    LABEL_RESTART,
    main_menu,
)

router = Router()

_WELCOME_PENDING_LIMIT = 5


def build_welcome_text(
    *,
    calendar_connected: bool,
    pending_tasks: list[Task],
) -> str:
    """Build the /start and /help dashboard message."""
    if calendar_connected:
        calendar_line = "📅 Calendar: *connected*"
    else:
        calendar_line = "📅 Calendar: *not connected* — tap Calendar to link"

    lines = [
        "Hey! I'm your personal to-do assistant.",
        "",
        calendar_line,
        "",
        "*Open tasks:*",
    ]
    if not pending_tasks:
        lines.append("_No open tasks. Use Quick or Guided to add one._")
    else:
        for task in pending_tasks:
            scheduled = (
                format_scheduled_at(task.scheduled_at) if task.scheduled_at else "—"
            )
            loc = f" ({task.location})" if task.location else ""
            lines.append(f"• {task.title} — {scheduled}{loc}")
        if len(pending_tasks) >= _WELCOME_PENDING_LIMIT:
            lines.append("_…more in My tasks_")

    lines.extend(
        [
            "",
            "⚡ *Quick task* — one message",
            "🧭 *Guided task* — step by step",
            "",
            "Use the buttons below to navigate.",
        ]
    )
    return "\n".join(lines)


async def _send_welcome(
    message: Message,
    registry: DatabaseRegistry,
) -> None:
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
            limit=_WELCOME_PENDING_LIMIT,
        )
    text = build_welcome_text(
        calendar_connected=calendar_connected,
        pending_tasks=pending,
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode="Markdown")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    await state.clear()
    await _send_welcome(message, registry)


@router.message(Command("help"))
async def cmd_help(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    await state.clear()
    await _send_welcome(message, registry)


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

    await cmd_tasks(message, registry)


@router.message(F.text == LABEL_CALENDAR)
async def menu_calendar(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    await state.clear()
    from app.todobot.handlers.calendar import cmd_connect_calendar

    await cmd_connect_calendar(message, registry)


@router.message(F.text == LABEL_HELP)
async def menu_help(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    await state.clear()
    await _send_welcome(message, registry)


@router.message(F.text == LABEL_RESTART)
async def menu_restart(
    message: Message,
    state: FSMContext,
    registry: DatabaseRegistry,
) -> None:
    """Clear FSM, delete tracked flow messages, and show a fresh /start welcome."""
    data = await state.get_data()
    msg_ids = data.get("_msg_ids", [])
    if msg_ids and message.bot:
        for msg_id in msg_ids:
            with suppress(Exception):
                await message.bot.delete_message(message.chat.id, msg_id)
    await state.clear()
    await _send_welcome(message, registry)
