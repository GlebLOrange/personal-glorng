"""Tests for one-shot capture gate and month busy grid."""

from datetime import UTC, date, datetime, time

from app.db.documents.task import Task, TaskStatus
from app.services.calendar import DEFAULT_EVENT_MINUTES, _build_event_body
from app.todobot.utils.nlp import ParsedTask
from app.todobot.utils.oneshot import (
    OneshotAction,
    format_month_grid,
    oneshot_action,
)


def test_oneshot_ignore_without_datetime() -> None:
    parsed = ParsedTask(title="buy milk", raw_text="buy milk")
    assert oneshot_action(parsed) == OneshotAction.IGNORE


def test_oneshot_save_when_complete() -> None:
    parsed = ParsedTask(
        title="dentist",
        date=date(2026, 10, 30),
        time=time(15, 0),
        raw_text="dentist Friday 15:00",
    )
    assert oneshot_action(parsed) == OneshotAction.SAVE


def test_oneshot_ask_when_partial_datetime() -> None:
    parsed = ParsedTask(
        title="dentist",
        date=date(2026, 10, 30),
        time=None,
        raw_text="dentist Friday",
    )
    assert oneshot_action(parsed) == OneshotAction.ASK


def test_oneshot_ask_when_datetime_missing_title() -> None:
    parsed = ParsedTask(
        title=None,
        date=date(2026, 10, 30),
        time=time(15, 0),
        raw_text="Friday 15:00",
    )
    assert oneshot_action(parsed) == OneshotAction.ASK


def test_event_body_uses_thirty_minute_end() -> None:
    task = Task(
        id=1,
        telegram_user_id=1,
        title="Call",
        scheduled_at=datetime(2026, 10, 30, 14, 0, tzinfo=UTC),
        status=TaskStatus.PENDING,
    )
    body = _build_event_body(task)
    assert body["start"]["dateTime"] == "2026-10-30T14:00:00Z"
    assert body["end"]["dateTime"] == "2026-10-30T14:30:00Z"
    assert DEFAULT_EVENT_MINUTES == 30


def test_month_grid_marks_busy_days() -> None:
    tasks = [
        Task(
            id=1,
            telegram_user_id=1,
            title="Dentist",
            scheduled_at=datetime(2026, 10, 3, 13, 0, tzinfo=UTC),
            status=TaskStatus.PENDING,
        ),
        Task(
            id=2,
            telegram_user_id=1,
            title="Gym",
            scheduled_at=datetime(2026, 10, 3, 7, 0, tzinfo=UTC),
            status=TaskStatus.PENDING,
        ),
        Task(
            id=3,
            telegram_user_id=1,
            title="Call",
            scheduled_at=datetime(2026, 10, 7, 16, 0, tzinfo=UTC),
            status=TaskStatus.PENDING,
        ),
    ]
    text = format_month_grid(
        year=2026,
        month=10,
        tasks=tasks,
        timezone_name="UTC",
    )
    assert "October 2026" in text
    assert " 3*" in text
    assert " 7*" in text
    assert "Busy days:" in text
    assert "Dentist" in text
    assert "Gym" in text
    assert "Call" in text
    # Empty day stays unmarked (day 1 in Oct 2026 is Thursday).
    assert " 1*" not in text


def test_month_grid_empty_month() -> None:
    text = format_month_grid(
        year=2026,
        month=11,
        tasks=[],
        timezone_name="UTC",
    )
    assert "No pending tasks this month." in text
