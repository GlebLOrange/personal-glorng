"""One-shot idle capture gate and month busy-grid formatting."""

from __future__ import annotations

from calendar import Calendar, month_name
from collections import defaultdict
from datetime import date, datetime, time
from enum import StrEnum

from app.db.documents.task import Task
from app.todobot.utils.nlp import ParsedTask


class OneshotAction(StrEnum):
    """What the idle-message path should do with a parse result."""

    IGNORE = "ignore"
    SAVE = "save"
    ASK = "ask"


def oneshot_action(parsed: ParsedTask) -> OneshotAction:
    """Gate: ignore chatter; save when complete; else ask once."""
    if parsed.date is None and parsed.time is None:
        return OneshotAction.IGNORE
    if parsed.is_complete:
        return OneshotAction.SAVE
    return OneshotAction.ASK


def clarification_prompt(parsed: ParsedTask) -> str:
    """One short question for the first missing required field."""
    missing = parsed.missing_fields
    if not missing:
        return "Looks complete — say that again to save."
    field = missing[0]
    if field == "title":
        return "What should I call this?"
    if field == "date":
        return "Which day?"
    return "What time?"


def merge_clarification(parsed: ParsedTask, reply: str, field: str) -> ParsedTask:
    """Apply a one-field clarification reply onto a draft parse."""
    from app.todobot.utils.nlp import parse_datetime_text, parse_task_input

    text = reply.strip()
    updated = ParsedTask(
        title=parsed.title,
        date=parsed.date,
        time=parsed.time,
        location=parsed.location,
        notes=parsed.notes,
        raw_text=parsed.raw_text,
    )
    if field == "title":
        if text:
            updated.title = text
        return updated

    dt = parse_datetime_text(text)
    if dt is not None:
        if field == "date":
            updated.date = dt.date()
            if updated.time is None and (dt.hour or dt.minute):
                updated.time = dt.time().replace(tzinfo=None)
        elif field == "time":
            updated.time = dt.time().replace(tzinfo=None)
            if updated.date is None:
                updated.date = dt.date()
        return updated

    extra = parse_task_input(text)
    if field == "date" and extra.date is not None:
        updated.date = extra.date
    if field == "time" and extra.time is not None:
        updated.time = extra.time
    if updated.title is None and extra.title:
        updated.title = extra.title
    if updated.location is None and extra.location:
        updated.location = extra.location
    return updated


def first_missing_field(parsed: ParsedTask) -> str | None:
    """Return the first required field still missing, if any."""
    missing = parsed.missing_fields
    return missing[0] if missing else None


def format_month_grid(
    *,
    year: int,
    month: int,
    tasks: list[Task],
    timezone_name: str,
) -> str:
    """Plain-text month grid; busy days marked with * and listed below."""
    from zoneinfo import ZoneInfo

    from app.core.utils import as_utc

    tz = ZoneInfo(timezone_name)
    busy: dict[int, list[Task]] = defaultdict(list)
    for task in tasks:
        local = as_utc(task.scheduled_at).astimezone(tz)
        if local.year == year and local.month == month:
            busy[local.day].append(task)

    cal = Calendar(firstweekday=0)  # Monday
    lines = [
        f"{month_name[month]} {year}",
        "Mo Tu We Th Fr Sa Su",
    ]
    for week in cal.monthdayscalendar(year, month):
        padded: list[str] = []
        for day in week:
            if day == 0:
                padded.append("   ")
            elif day in busy:
                padded.append(f"{day:2d}*")
            else:
                padded.append(f"{day:2d} ")
        lines.append(" ".join(padded).rstrip())

    lines.append("")
    if not busy:
        lines.append("No pending tasks this month.")
        return "\n".join(lines)

    lines.append("Busy days:")
    for day in sorted(busy):
        parts: list[str] = []
        for task in sorted(busy[day], key=lambda t: as_utc(t.scheduled_at)):
            local = as_utc(task.scheduled_at).astimezone(tz)
            parts.append(f"{task.title} {local.strftime('%H:%M')}")
        lines.append(f"• {day} — {', '.join(parts)}")
    return "\n".join(lines)


def scheduled_at_from_parsed(parsed: ParsedTask) -> datetime:
    """Build UTC scheduled_at from a complete ParsedTask."""
    from app.core.utils import local_naive_to_utc

    if parsed.date is None or parsed.time is None:
        msg = "date and time are required"
        raise ValueError(msg)
    wall = datetime.combine(parsed.date, parsed.time)
    return local_naive_to_utc(wall)


def parsed_from_fsm(data: dict[str, object]) -> ParsedTask:
    """Rebuild ParsedTask from FSM data keys."""
    date_raw = data.get("date")
    time_raw = data.get("time")
    task_date = date.fromisoformat(str(date_raw)) if date_raw else None
    task_time: time | None = None
    if time_raw:
        hour, minute = str(time_raw).split(":", 1)
        task_time = time(int(hour), int(minute))
    title = data.get("title")
    location = data.get("location")
    notes = data.get("notes")
    return ParsedTask(
        title=str(title) if title else None,
        date=task_date,
        time=task_time,
        location=str(location) if location else None,
        notes=str(notes) if notes else None,
        raw_text=str(data.get("raw_text") or ""),
    )


def parsed_to_fsm(parsed: ParsedTask) -> dict[str, object]:
    """Serialize ParsedTask into FSM-friendly scalars."""
    payload: dict[str, object] = {"raw_text": parsed.raw_text}
    if parsed.title:
        payload["title"] = parsed.title
    if parsed.date:
        payload["date"] = parsed.date.isoformat()
    if parsed.time:
        payload["time"] = parsed.time.strftime("%H:%M")
    if parsed.location:
        payload["location"] = parsed.location
    if parsed.notes:
        payload["notes"] = parsed.notes
    return payload
