"""Persistent reply-keyboard main menu and welcome inline CTAs."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

LABEL_QUICK_TASK = "⚡ quick task"
LABEL_GUIDED_TASK = "🧭 guided task"
LABEL_MY_TASKS = "📋 list tasks"
LABEL_CALENDAR = "📅 calendar"
LABEL_HELP = "❓ help"
LABEL_RESTART = "🔄 restart"
# Kept for expense module imports; expenses are hidden from the menu.
LABEL_LOG_EXPENSE = "Log expense"
# Backward-compatible alias (maps to quick AI intake).
LABEL_NEW_TASK = LABEL_QUICK_TASK

ALL_LABELS = {
    LABEL_QUICK_TASK,
    LABEL_GUIDED_TASK,
    LABEL_MY_TASKS,
    LABEL_CALENDAR,
    LABEL_HELP,
    LABEL_RESTART,
}


def main_menu() -> ReplyKeyboardMarkup:
    """Build the persistent main menu keyboard (same order as welcome inline)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=LABEL_QUICK_TASK),
                KeyboardButton(text=LABEL_GUIDED_TASK),
            ],
            [KeyboardButton(text=LABEL_MY_TASKS)],
            [KeyboardButton(text=LABEL_CALENDAR)],
            [KeyboardButton(text=LABEL_HELP), KeyboardButton(text=LABEL_RESTART)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def welcome_inline(*, calendar_connected: bool) -> InlineKeyboardMarkup:
    """Fixed welcome menu: quick/guided, list tasks, calendar, help/restart."""
    calendar_btn = (
        InlineKeyboardButton(text="📅 calendar", callback_data="w:cal")
        if calendar_connected
        else InlineKeyboardButton(
            text="📅 connect calendar",
            callback_data="w:connect",
        )
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚡ quick task", callback_data="w:quick"),
                InlineKeyboardButton(text="🧭 guided task", callback_data="w:guided"),
            ],
            [
                InlineKeyboardButton(text="📋 list tasks", callback_data="w:tasks"),
            ],
            [calendar_btn],
            [
                InlineKeyboardButton(text="❓ help", callback_data="w:help"),
                InlineKeyboardButton(text="🔄 restart", callback_data="w:restart"),
            ],
        ],
    )
