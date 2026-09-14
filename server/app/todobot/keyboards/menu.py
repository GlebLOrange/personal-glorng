"""Persistent reply-keyboard main menu."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

LABEL_QUICK_TASK = "⚡ Quick task"
LABEL_GUIDED_TASK = "🧭 Guided task"
LABEL_MY_TASKS = "📋 My tasks"
LABEL_CALENDAR = "📅 Calendar"
LABEL_HELP = "❓ Help"
LABEL_RESTART = "🔄 Restart"
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
    """Build the persistent main menu keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=LABEL_QUICK_TASK),
                KeyboardButton(text=LABEL_GUIDED_TASK),
            ],
            [
                KeyboardButton(text=LABEL_MY_TASKS),
                KeyboardButton(text=LABEL_CALENDAR),
            ],
            [KeyboardButton(text=LABEL_HELP), KeyboardButton(text=LABEL_RESTART)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
