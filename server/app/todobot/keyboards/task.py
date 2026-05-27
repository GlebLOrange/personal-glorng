"""Inline keyboard builders for task creation and management."""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.settings import get_settings

_TIME_SLOTS = [
    ("Morning (09:00)", "🌅", "time:09:00", time(9, 0)),
    ("Afternoon (14:00)", "☀️", "time:14:00", time(14, 0)),
    ("Evening (18:00)", "🌆", "time:18:00", time(18, 0)),
]


def _now_in_tz() -> datetime:
    """Current datetime in the configured timezone."""
    return datetime.now(ZoneInfo(get_settings().TIMEZONE))


def date_picker() -> InlineKeyboardMarkup:
    today = _now_in_tz().date()
    tomorrow = today + timedelta(days=1)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"📅 Today ({today.strftime('%b %d')})",
                    callback_data=f"date:{today.isoformat()}",
                ),
                InlineKeyboardButton(
                    text=f"📅 Tomorrow ({tomorrow.strftime('%b %d')})",
                    callback_data=f"date:{tomorrow.isoformat()}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗓 Pick date...",
                    callback_data="date:custom",
                ),
            ],
        ],
    )


def time_picker(selected_date: str | None = None) -> InlineKeyboardMarkup:
    """Build time picker, graying out past slots when date is today."""
    now = _now_in_tz()
    is_today = selected_date == now.date().isoformat() if selected_date else False

    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for label, emoji, callback_data, slot_time in _TIME_SLOTS:
        if is_today and now.time() >= slot_time:
            text = f"⚪ {label}"
        else:
            text = f"{emoji} {label}"
        row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    rows.append([
        InlineKeyboardButton(text="⏰ Custom time...", callback_data="time:custom"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def reminder_presets() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏰ 15 min", callback_data="remind:15"),
                InlineKeyboardButton(text="⏰ 30 min", callback_data="remind:30"),
                InlineKeyboardButton(text="⏰ 1 hour", callback_data="remind:60"),
            ],
            [
                InlineKeyboardButton(text="⏰ 3 hours", callback_data="remind:180"),
                InlineKeyboardButton(text="🔕 No reminder", callback_data="remind:none"),
            ],
        ],
    )


def confirmation() -> InlineKeyboardMarkup:
    """Build confirm/edit/cancel buttons."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Confirm", callback_data="confirm:yes",
                ),
                InlineKeyboardButton(
                    text="✏️ Edit", callback_data="confirm:edit",
                ),
                InlineKeyboardButton(
                    text="❌ Cancel", callback_data="confirm:cancel",
                ),
            ],
        ],
    )


def completion_options(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Completed",
                    callback_data=f"status:{task_id}:completed",
                ),
                InlineKeyboardButton(
                    text="⬜ Not completed",
                    callback_data=f"status:{task_id}:not_completed",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏭ Postponed",
                    callback_data=f"status:{task_id}:postponed",
                ),
            ],
        ],
    )


def reminder_actions(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Complete",
                    callback_data=f"raction:{task_id}:complete",
                ),
                InlineKeyboardButton(
                    text="⏰ Snooze 15m",
                    callback_data=f"raction:{task_id}:snooze:15",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏰ Snooze 30m",
                    callback_data=f"raction:{task_id}:snooze:30",
                ),
                InlineKeyboardButton(
                    text="⏰ Snooze 1h",
                    callback_data=f"raction:{task_id}:snooze:60",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📅 Postpone...",
                    callback_data=f"raction:{task_id}:postpone",
                ),
            ],
        ],
    )


def skip_button(field: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏩ Skip",
                    callback_data=f"skip:{field}",
                ),
            ],
        ],
    )
