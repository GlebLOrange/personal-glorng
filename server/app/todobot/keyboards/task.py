"""Inline keyboard builders for task creation and management."""

from datetime import datetime, time, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.utils import format_display_date, local_now

_TIME_SLOTS = [
    ("Morning (09:00)", "🌅", "time:09:00", time(9, 0)),
    ("Afternoon (14:00)", "☀️", "time:14:00", time(14, 0)),
    ("Evening (18:00)", "🌆", "time:18:00", time(18, 0)),
]


def _now_in_tz() -> datetime:
    """Current datetime in the configured timezone."""
    return local_now()


def date_picker() -> InlineKeyboardMarkup:
    today = _now_in_tz().date()
    tomorrow = today + timedelta(days=1)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"📅 Today ({format_display_date(today)})",
                    callback_data=f"date:{today.isoformat()}",
                ),
                InlineKeyboardButton(
                    text=f"📅 Tomorrow ({format_display_date(tomorrow)})",
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

    rows.append(
        [
            InlineKeyboardButton(text="⏰ Custom time...", callback_data="time:custom"),
        ]
    )

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
                InlineKeyboardButton(
                    text="🔕 No reminder",
                    callback_data="remind:none",
                ),
            ],
        ],
    )


def confirmation() -> InlineKeyboardMarkup:
    """Build confirm/edit/cancel buttons."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Confirm",
                    callback_data="confirm:yes",
                ),
                InlineKeyboardButton(
                    text="✏️ Edit",
                    callback_data="confirm:edit",
                ),
                InlineKeyboardButton(
                    text="❌ Cancel",
                    callback_data="confirm:cancel",
                ),
            ],
        ],
    )


def completion_options(task_id: int) -> InlineKeyboardMarkup:
    """Status buttons for reminder-era flows (not My tasks)."""
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


def my_tasks_list(tasks: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    """One button per task: (task_id, label)."""
    rows = [
        [
            InlineKeyboardButton(
                text=label[:64],
                callback_data=f"mt:o:{task_id}",
            ),
        ]
        for task_id, label in tasks
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def my_task_detail(task_id: int) -> InlineKeyboardMarkup:
    """Detail screen: Remove | Edit / Back | Main."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Remove", callback_data=f"mt:rm:{task_id}"),
                InlineKeyboardButton(text="Edit", callback_data=f"mt:e:{task_id}"),
            ],
            [
                InlineKeyboardButton(text="Back", callback_data="mt:back"),
                InlineKeyboardButton(text="Main", callback_data="mt:main"),
            ],
        ],
    )


def my_task_remove_choices(task_id: int) -> InlineKeyboardMarkup:
    """Cancel or didn't finish; both allowed for future tasks."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Cancel task",
                    callback_data=f"mt:c:{task_id}:cancelled",
                ),
                InlineKeyboardButton(
                    text="Didn't finish",
                    callback_data=f"mt:c:{task_id}:not_completed",
                ),
            ],
            [
                InlineKeyboardButton(text="Back", callback_data=f"mt:o:{task_id}"),
            ],
        ],
    )


def my_task_date_picker(task_id: int) -> InlineKeyboardMarkup:
    """Date picker for My tasks edit (separate callback prefix)."""
    today = _now_in_tz().date()
    tomorrow = today + timedelta(days=1)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"📅 Today ({format_display_date(today)})",
                    callback_data=f"mt:d:{task_id}:{today.isoformat()}",
                ),
                InlineKeyboardButton(
                    text=f"📅 Tomorrow ({format_display_date(tomorrow)})",
                    callback_data=f"mt:d:{task_id}:{tomorrow.isoformat()}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗓 Pick date...",
                    callback_data=f"mt:d:{task_id}:custom",
                ),
                InlineKeyboardButton(text="Back", callback_data=f"mt:o:{task_id}"),
            ],
        ],
    )


def my_task_time_picker(
    task_id: int,
    selected_date: str | None = None,
) -> InlineKeyboardMarkup:
    """Time picker for My tasks edit (separate callback prefix)."""
    now = _now_in_tz()
    is_today = selected_date == now.date().isoformat() if selected_date else False

    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for label, emoji, _callback, slot_time in _TIME_SLOTS:
        hhmm = slot_time.strftime("%H-%M")
        if is_today and now.time() >= slot_time:
            text = f"⚪ {label}"
        else:
            text = f"{emoji} {label}"
        row.append(
            InlineKeyboardButton(
                text=text,
                callback_data=f"mt:t:{task_id}:{hhmm}",
            ),
        )
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append(
        [
            InlineKeyboardButton(
                text="⏰ Custom time...",
                callback_data=f"mt:t:{task_id}:custom",
            ),
            InlineKeyboardButton(text="Back", callback_data=f"mt:o:{task_id}"),
        ],
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


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
