"""Lightweight NLP parsing for task creation from natural language."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time

import dateparser

from app.settings import get_settings

_LOCATION_PATTERNS = [
    re.compile(r"\b(?:at|@)\s+(.+?)(?:\.|,|$)", re.IGNORECASE),
    re.compile(r"\bnear\s+(.+?)(?:\.|,|$)", re.IGNORECASE),
    re.compile(r"\bin\s+(?:the\s+)?(.+?)(?:\.|,|$)", re.IGNORECASE),
]


@dataclass
class ParsedTask:
    """Result of NL parsing -- None fields need follow-up questions."""

    title: str | None = None
    date: date | None = None
    time: time | None = None
    location: str | None = None
    notes: str | None = None
    raw_text: str = ""
    _consumed_spans: list[tuple[int, int]] = field(
        default_factory=list,
        repr=False,
    )

    @property
    def missing_fields(self) -> list[str]:
        required = ["title", "date", "time"]
        return [f for f in required if getattr(self, f) is None]

    @property
    def is_complete(self) -> bool:
        return not self.missing_fields


def _extract_datetime(text: str) -> tuple[datetime | None, str]:
    """Try to parse a date/time from text, return parsed dt and remaining text."""
    settings = get_settings()
    parser_settings: dict[str, object] = {
        "PREFER_DATES_FROM": "future",
        "RETURN_AS_TIMEZONE_AWARE": True,
        "TIMEZONE": settings.TIMEZONE,
        "RELATIVE_BASE": datetime.now(),
    }

    parsed = dateparser.parse(text, settings=parser_settings)
    if not parsed:
        return None, text

    cleaned = dateparser.parse(
        text,
        settings={**parser_settings, "RETURN_AS_TIMEZONE_AWARE": False},
    )

    remaining = text
    if cleaned:
        for token in _datetime_tokens(text):
            test = dateparser.parse(token, settings=parser_settings)
            if test:
                remaining = remaining.replace(token, "", 1).strip()

    return parsed, remaining


def _datetime_tokens(text: str) -> list[str]:
    """Generate candidate date/time substrings to try parsing."""
    words = text.split()
    candidates = []
    for length in range(len(words), 0, -1):
        for start in range(len(words) - length + 1):
            candidates.append(" ".join(words[start : start + length]))
    return candidates


def _extract_location(text: str) -> tuple[str | None, str]:
    """Extract location from text using pattern matching."""
    for pattern in _LOCATION_PATTERNS:
        match = pattern.search(text)
        if match:
            location = match.group(1).strip()
            if len(location) > 2:
                remaining = text[: match.start()] + text[match.end() :]
                return location, remaining.strip()
    return None, text


def parse_task_input(text: str) -> ParsedTask:
    """Parse free-form text into structured task fields."""
    result = ParsedTask(raw_text=text)

    parsed_dt, remaining = _extract_datetime(text)
    if parsed_dt:
        result.date = parsed_dt.date()
        if parsed_dt.hour != 0 or parsed_dt.minute != 0:
            result.time = parsed_dt.time().replace(tzinfo=None)

    location, remaining = _extract_location(remaining)
    if location:
        result.location = location

    title = remaining.strip(" .,;:-")
    if title:
        result.title = title

    return result
