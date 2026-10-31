"""Single copy source for TodoBot /help catalog and callback toasts."""

from __future__ import annotations

# Telegram toast text limit; keep strings short (~40–60).
_TOAST_LIMIT = 200

HELP_SECTIONS: list[tuple[str, list[str]]] = [
    (
        "Capture",
        [
            "• *quick task* — one message; clarify if needed; always confirm",
            "• *guided task* — title → date → time → optional details → confirm",
            '• *idle message* — e.g. "Friday 15:00 dentist" saves when complete',
            "• *confirm* / *edit* / *cancel* — save, change fields, or abort",
            "• *skip* — skip optional location or notes",
            "• *back* — step back one field in guided flow",
        ],
    ),
    (
        "Manage",
        [
            "• *tasks* — open closest open tasks",
            "• *mark done* — complete from the task detail",
            "• *remove* — mark cancelled or not completed",
            "• *edit* — change title, when (date/time), location, or notes",
            "• *main* — return to the welcome dashboard",
        ],
    ),
    (
        "Calendar",
        [
            "• *connect* — link Google Calendar once",
            "• *hub* — Sync now, this month, or open a day",
            "• New tasks enqueue Calendar events when linked",
        ],
    ),
    (
        "Reminders",
        [
            "• At-start ping always; optional early remind on Quick/Guided",
            "• *complete* — mark done from a reminder",
            "• *snooze* 15 / 30 / 60 — ping only (keeps scheduled time)",
            "• *postpone* — presets (+1h, tomorrow 09:00) or custom date/time",
        ],
    ),
    (
        "Navigation",
        [
            "• *help* — this catalog · *restart* — clear a flow and refresh",
            "• Slash: /start · /help · /new · /tasks · /month · /connect_calendar",
        ],
    ),
]

_W_TOASTS: dict[str, str] = {
    "quick": "Quick task — one message",
    "guided": "Guided — step by step",
    "tasks": "Opening tasks",
    "cal": "Opening calendar",
    "connect": "Connect Google Calendar",
    "help": "Opening help",
    "restart": "Restarting…",
}

_CONFIRM_TOASTS: dict[str, str] = {
    "yes": "Saving task…",
    "edit": "Choose a field",
    "cancel": "Cancelled",
}

_FLOW_TOASTS: dict[str, str] = {
    "cancel": "Cancelled",
    "back": "Going back",
}

_EDITF_TOASTS: dict[str, str] = {
    "title": "Edit title",
    "date": "Edit date",
    "time": "Edit time",
    "back": "Back to confirm",
}

_CAL_TOASTS: dict[str, str] = {
    "hub": "Calendar hub",
    "month": "This month",
    "sync": "Syncing…",
}

_PP_TOASTS: dict[str, str] = {
    "1h": "Postpone +1 hour",
    "tm09": "Tomorrow 09:00",
    "custom": "Type a date/time",
}

_STATUS_TOASTS: dict[str, str] = {
    "completed": "Marked completed",
    "not_completed": "Marked not completed",
    "postponed": "Marked postponed",
}

_MT_ACTION_TOASTS: dict[str, str] = {
    "back": "Back to list",
    "main": "Main menu",
    "done": "Marked done",
    "o": "Opening task",
    "rm": "Remove options",
    "e": "Edit task",
    "ew": "Change when",
}

_MT_EF_TOASTS: dict[str, str] = {
    "title": "Edit title",
    "location": "Edit location",
    "notes": "Edit notes",
}

_RACTION_TOASTS: dict[str, str] = {
    "complete": "Completing…",
    "postpone": "Postpone…",
}

_SNOOZE_TOASTS: dict[str, str] = {
    "15": "Snooze 15 min",
    "30": "Snooze 30 min",
    "60": "Snooze 60 min",
}


def help_catalog_lines() -> list[str]:
    """Markdown section lines for ``build_help_text`` (no title/timezone)."""
    lines: list[str] = []
    for index, (heading, bullets) in enumerate(HELP_SECTIONS):
        if index:
            lines.append("")
        lines.append(f"*{heading}*")
        lines.extend(bullets)
    return lines


def _clip(text: str) -> str:
    if len(text) <= _TOAST_LIMIT:
        return text
    return text[: _TOAST_LIMIT - 1] + "…"


def _toast_mt(callback_data: str) -> str | None:
    parts = callback_data.split(":")
    if len(parts) < 2:
        return None
    action = parts[1]
    if action in {"back", "main"}:
        return _MT_ACTION_TOASTS[action]
    if action in {"done", "o", "rm", "e", "ew"}:
        return _MT_ACTION_TOASTS.get(action)
    if action == "c":
        return "Updating status…"
    if action == "ef" and len(parts) >= 4:
        return _MT_EF_TOASTS.get(parts[3], "Edit field")
    if action == "d" and len(parts) >= 4:
        value = parts[3]
        if value == "custom":
            return "Type a date"
        return "Date set"
    if action == "t" and len(parts) >= 4:
        value = parts[3]
        if value == "custom":
            return "Type a time"
        return "Time set"
    return None


def _toast_cal(callback_data: str) -> str | None:
    parts = callback_data.split(":")
    if len(parts) < 2:
        return None
    action = parts[1]
    if action == "day":
        return "Day agenda"
    return _CAL_TOASTS.get(action)


def _toast_raction(callback_data: str) -> str | None:
    parts = callback_data.split(":")
    if len(parts) < 3:
        return None
    action = parts[2]
    if action == "snooze" and len(parts) >= 4:
        return _SNOOZE_TOASTS.get(parts[3], "Snoozed")
    return _RACTION_TOASTS.get(action)


def _toast_status(callback_data: str) -> str | None:
    parts = callback_data.split(":")
    if len(parts) != 3:
        return None
    return _STATUS_TOASTS.get(parts[2])


def toast_for(callback_data: str) -> str | None:
    """Return a short Telegram toast for ``callback_data``, or ``None``."""
    if not callback_data:
        return None

    if callback_data.startswith("date:"):
        value = callback_data.removeprefix("date:")
        text = "Type a date" if value == "custom" else "Date set"
        return _clip(text)

    if callback_data.startswith("time:"):
        value = callback_data.removeprefix("time:")
        text = "Type a time" if value == "custom" else "Time set"
        return _clip(text)

    if callback_data.startswith("w:"):
        text = _W_TOASTS.get(callback_data.removeprefix("w:"))
        return _clip(text) if text else None

    if callback_data.startswith("skip:"):
        return _clip("Skipped")

    if callback_data.startswith("confirm:"):
        text = _CONFIRM_TOASTS.get(callback_data.removeprefix("confirm:"))
        return _clip(text) if text else None

    if callback_data.startswith("flow:"):
        text = _FLOW_TOASTS.get(callback_data.removeprefix("flow:"))
        return _clip(text) if text else None

    if callback_data.startswith("editf:"):
        text = _EDITF_TOASTS.get(callback_data.removeprefix("editf:"), "Edit field")
        return _clip(text)

    if callback_data.startswith("mt:"):
        text = _toast_mt(callback_data)
        return _clip(text) if text else None

    if callback_data.startswith("cal:"):
        text = _toast_cal(callback_data)
        return _clip(text) if text else None

    if callback_data.startswith("raction:"):
        text = _toast_raction(callback_data)
        return _clip(text) if text else None

    if callback_data.startswith("pp:"):
        text = _PP_TOASTS.get(callback_data.removeprefix("pp:"))
        return _clip(text) if text else None

    if callback_data.startswith("status:"):
        text = _toast_status(callback_data)
        return _clip(text) if text else None

    return None
