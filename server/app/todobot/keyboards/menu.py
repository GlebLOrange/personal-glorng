"""Persistent reply-keyboard main menu."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

LABEL_NEW_TASK = "New Task"
LABEL_MY_TASKS = "My Tasks"
LABEL_CALENDAR = "Calendar"
LABEL_HELP = "Help"
LABEL_RESTART = "🔄 Restart"

ALL_LABELS = {LABEL_NEW_TASK, LABEL_MY_TASKS, LABEL_CALENDAR, LABEL_HELP, LABEL_RESTART}


def main_menu() -> ReplyKeyboardMarkup:
    """Build the persistent main menu keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=LABEL_NEW_TASK), KeyboardButton(text=LABEL_MY_TASKS)],
            [KeyboardButton(text=LABEL_CALENDAR), KeyboardButton(text=LABEL_HELP)],
            [KeyboardButton(text=LABEL_RESTART)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
