"""Start, help, and main-menu button handlers."""

from contextlib import suppress

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.todobot.keyboards.menu import (
    LABEL_CALENDAR,
    LABEL_HELP,
    LABEL_MY_TASKS,
    LABEL_NEW_TASK,
    LABEL_RESTART,
    main_menu,
)

router = Router()

WELCOME_TEXT = (
    "Hey! I'm your personal reminder assistant.\n\n"
    "You can create tasks in two ways:\n"
    '1. /new — send one message: "Tomorrow at 18:00 gym near city center"\n'
    "2. /new guided — step-by-step flow\n\n"
    "Log expenses quickly:\n"
    '• /spend 89.50 biedronka — one message\n'
    "• /spend — step-by-step\n"
    "• /expenses — this month's total\n\n"
    "Use the menu buttons below to navigate."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu(), parse_mode="Markdown")


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu(), parse_mode="Markdown")


@router.message(F.text == LABEL_NEW_TASK)
async def menu_new_task(message: Message, state: FSMContext) -> None:
    await state.clear()
    from app.todobot.handlers.task_create import cmd_new_task

    await cmd_new_task(message, state)


@router.message(F.text == LABEL_MY_TASKS)
async def menu_my_tasks(message: Message, state: FSMContext, db: AsyncSession) -> None:
    await state.clear()
    from app.todobot.handlers.task_manage import cmd_tasks

    await cmd_tasks(message, db)


@router.message(F.text == LABEL_CALENDAR)
async def menu_calendar(message: Message, state: FSMContext) -> None:
    await state.clear()
    from app.todobot.handlers.calendar import cmd_connect_calendar

    await cmd_connect_calendar(message)


@router.message(F.text == LABEL_HELP)
async def menu_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu(), parse_mode="Markdown")


@router.message(F.text == LABEL_RESTART)
async def menu_restart(message: Message, state: FSMContext) -> None:
    """Clear FSM state and delete tracked flow messages."""
    data = await state.get_data()
    msg_ids = data.get("_msg_ids", [])
    if msg_ids and message.bot:
        for msg_id in msg_ids:
            with suppress(Exception):
                await message.bot.delete_message(message.chat.id, msg_id)
    await state.clear()
    await message.answer(
        "🔄 Bot restarted. How can I help?",
        reply_markup=main_menu(),
    )
