"""Inline keyboard builders for task creation and management."""

from datetime import datetime, time, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.utils import format_display_date, local_now

_TIME_SLOTS = [
    ("morning (09:00)", "🌅", "time:09:00", time(9, 0)),
    ("afternoon (14:00)", "☀️", "time:14:00", time(14, 0)),
    ("evening (18:00)", "🌆", "time:18:00", time(18, 0)),
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
                    text=f"📅 today ({format_display_date(today)})",
                    callback_data=f"date:{today.isoformat()}",
                ),
                InlineKeyboardButton(
                    text=f"📅 tomorrow ({format_display_date(tomorrow)})",
                    callback_data=f"date:{tomorrow.isoformat()}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗓 pick date…",
                    callback_data="date:custom",
                ),
            ],
        ],
    )


def time_picker(
    selected_date: str | None = None,
    *,
    block_past: bool = True,
) -> InlineKeyboardMarkup:
    """Build time picker; past slots on today are omitted when block_past is set."""
    now = _now_in_tz()
    is_today = selected_date == now.date().isoformat() if selected_date else False

    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for label, emoji, callback_data, slot_time in _TIME_SLOTS:
        if is_today and now.time() >= slot_time:
            if block_past:
                continue
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
            InlineKeyboardButton(text="⏰ custom time…", callback_data="time:custom"),
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
                    text="🔕 no reminder",
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
                    text="✅ confirm",
                    callback_data="confirm:yes",
                ),
                InlineKeyboardButton(
                    text="✏️ edit",
                    callback_data="confirm:edit",
                ),
                InlineKeyboardButton(
                    text="❌ cancel",
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
                    text="✅ completed",
                    callback_data=f"status:{task_id}:completed",
                ),
                InlineKeyboardButton(
                    text="⬜ not completed",
                    callback_data=f"status:{task_id}:not_completed",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏭ postponed",
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
    """Detail screen: mark done | remove | edit / back | main."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ mark done",
                    callback_data=f"mt:done:{task_id}",
                ),
                InlineKeyboardButton(
                    text="🗑 remove",
                    callback_data=f"mt:rm:{task_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✏️ edit",
                    callback_data=f"mt:e:{task_id}",
                ),
            ],
            [
                InlineKeyboardButton(text="◀️ back", callback_data="mt:back"),
                InlineKeyboardButton(text="🏠 main", callback_data="mt:main"),
            ],
        ],
    )


def my_task_edit_fields(task_id: int) -> InlineKeyboardMarkup:
    """Choose which fields to edit on a task."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ title",
                    callback_data=f"mt:ef:{task_id}:title",
                ),
                InlineKeyboardButton(
                    text="📅 when",
                    callback_data=f"mt:ew:{task_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📍 location",
                    callback_data=f"mt:ef:{task_id}:location",
                ),
                InlineKeyboardButton(
                    text="📝 notes",
                    callback_data=f"mt:ef:{task_id}:notes",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ back",
                    callback_data=f"mt:o:{task_id}",
                ),
            ],
        ],
    )


def my_task_remove_choices(task_id: int) -> InlineKeyboardMarkup:
    """Cancel or didn't finish; both allowed for future tasks."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 cancel task",
                    callback_data=f"mt:c:{task_id}:cancelled",
                ),
                InlineKeyboardButton(
                    text="⬜ didn't finish",
                    callback_data=f"mt:c:{task_id}:not_completed",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ back",
                    callback_data=f"mt:o:{task_id}",
                ),
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
                    text=f"📅 today ({format_display_date(today)})",
                    callback_data=f"mt:d:{task_id}:{today.isoformat()}",
                ),
                InlineKeyboardButton(
                    text=f"📅 tomorrow ({format_display_date(tomorrow)})",
                    callback_data=f"mt:d:{task_id}:{tomorrow.isoformat()}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗓 pick date…",
                    callback_data=f"mt:d:{task_id}:custom",
                ),
                InlineKeyboardButton(
                    text="◀️ back",
                    callback_data=f"mt:o:{task_id}",
                ),
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
            continue  # block past slots
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
                text="⏰ custom time…",
                callback_data=f"mt:t:{task_id}:custom",
            ),
            InlineKeyboardButton(
                text="◀️ back",
                callback_data=f"mt:o:{task_id}",
            ),
        ],
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def reminder_actions(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ complete",
                    callback_data=f"raction:{task_id}:complete",
                ),
                InlineKeyboardButton(
                    text="⏰ snooze 15m",
                    callback_data=f"raction:{task_id}:snooze:15",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏰ snooze 30m",
                    callback_data=f"raction:{task_id}:snooze:30",
                ),
                InlineKeyboardButton(
                    text="⏰ snooze 1h",
                    callback_data=f"raction:{task_id}:snooze:60",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📅 postpone…",
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
                    text="⏩ skip",
                    callback_data=f"skip:{field}",
                ),
                InlineKeyboardButton(text="❌ cancel", callback_data="flow:cancel"),
            ],
            [
                InlineKeyboardButton(text="◀️ back", callback_data="flow:back"),
            ],
        ],
    )


def flow_nav(*, include_skip: str | None = None) -> InlineKeyboardMarkup:
    """Back + Cancel, optional Skip for optional fields."""
    rows: list[list[InlineKeyboardButton]] = []
    if include_skip:
        rows.append(
            [
                InlineKeyboardButton(
                    text="⏩ skip",
                    callback_data=f"skip:{include_skip}",
                ),
            ],
        )
    rows.append(
        [
            InlineKeyboardButton(text="◀️ back", callback_data="flow:back"),
            InlineKeyboardButton(text="❌ cancel", callback_data="flow:cancel"),
        ],
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def with_flow_nav(base: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    """Append Back/Cancel rows to an existing picker keyboard."""
    rows = [list(row) for row in base.inline_keyboard]
    rows.append(
        [
            InlineKeyboardButton(text="◀️ back", callback_data="flow:back"),
            InlineKeyboardButton(text="❌ cancel", callback_data="flow:cancel"),
        ],
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def field_edit_menu() -> InlineKeyboardMarkup:
    """Field-level edit after confirm."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ title", callback_data="editf:title"),
                InlineKeyboardButton(text="📅 date", callback_data="editf:date"),
                InlineKeyboardButton(text="⏰ time", callback_data="editf:time"),
            ],
            [
                InlineKeyboardButton(text="◀️ back", callback_data="editf:back"),
                InlineKeyboardButton(text="❌ cancel", callback_data="flow:cancel"),
            ],
        ],
    )


def clarify_cancel() -> InlineKeyboardMarkup:
    """Cancel during AI/oneshot clarification."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ cancel", callback_data="flow:cancel")],
        ],
    )


def postpone_presets() -> InlineKeyboardMarkup:
    """Reminder postpone: presets + custom."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="+1 hour", callback_data="pp:1h"),
                InlineKeyboardButton(text="tomorrow 09:00", callback_data="pp:tm09"),
            ],
            [
                InlineKeyboardButton(
                    text="custom…",
                    callback_data="pp:custom",
                ),
            ],
        ],
    )


def calendar_hub(*, reconnect_url: str | None) -> InlineKeyboardMarkup:
    """Connected calendar status hub."""
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="🔄 sync now", callback_data="cal:sync"),
            InlineKeyboardButton(text="📆 this month", callback_data="cal:month"),
        ],
    ]
    if reconnect_url:
        rows.append(
            [
                InlineKeyboardButton(
                    text="🔗 reconnect google",
                    url=reconnect_url,
                ),
            ],
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def month_day_buttons(
    *,
    year: int,
    month: int,
    busy_days: list[int],
) -> InlineKeyboardMarkup:
    """Interactive day buttons for busy days in the current month."""
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for day in busy_days:
        row.append(
            InlineKeyboardButton(
                text=f"{day}*",
                callback_data=f"cal:day:{year}-{month:02d}-{day:02d}",
            ),
        )
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append(
        [InlineKeyboardButton(text="◀️ hub", callback_data="cal:hub")],
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
