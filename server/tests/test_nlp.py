"""Tests for task NLP parser."""

from datetime import date

from app.todobot.utils.nlp import ParsedTask, parse_task_input


def test_parse_title_only_missing_date_and_time() -> None:
    parsed = parse_task_input("do something important")
    assert parsed.title
    assert parsed.date is None
    assert parsed.time is None
    assert "date" in parsed.missing_fields
    assert "time" in parsed.missing_fields
    assert not parsed.is_complete


def test_parse_at_pattern_extracts_location_before_datetime() -> None:
    parsed = parse_task_input("Buy milk tomorrow at 10:30")
    assert parsed.title == "Buy milk tomorrow"
    assert parsed.location == "10:30"


def test_parse_location_at_pattern() -> None:
    parsed = parse_task_input("Dentist Friday 10am at Main Street clinic")
    assert parsed.location is not None
    assert "main street" in parsed.location.lower()


def test_parse_location_near_pattern() -> None:
    parsed = parse_task_input("Run near the river tomorrow 7am")
    assert parsed.location is not None


def test_at_pattern_can_capture_trailing_phrase() -> None:
    parsed = parse_task_input("Tomorrow at 18:00 gym")
    assert parsed.title == "Tomorrow"
    assert parsed.location == "18:00 gym"


def test_missing_fields_property() -> None:
    task = ParsedTask(title="Only title", date=date(2026, 6, 1))
    assert task.missing_fields == ["time"]
    assert not task.is_complete
