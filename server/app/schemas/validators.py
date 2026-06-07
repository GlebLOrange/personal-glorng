"""Reusable Pydantic field validators."""

from datetime import datetime
from typing import Annotated

from pydantic import BeforeValidator

from app.core.text import sanitize_optional_text, sanitize_text
from app.core.utils import as_utc


def validate_clean_required(
    value: str,
    *,
    max_length: int | None = None,
    field_name: str = "Text",
) -> str:
    """Strip control chars, normalize whitespace, and reject empty result."""
    cleaned = sanitize_text(value, max_length=max_length)
    if not cleaned:
        msg = f"{field_name} must not be empty"
        raise ValueError(msg)
    return cleaned


def validate_clean_optional(
    value: str | None,
    *,
    max_length: int | None = None,
) -> str | None:
    """Sanitize optional text; return None when empty after cleaning."""
    return sanitize_optional_text(value, max_length=max_length)


def validate_clean_string_list(
    value: list[str],
    *,
    item_max_length: int | None = None,
    field_name: str = "Item",
) -> list[str]:
    """Sanitize each non-empty string in a list."""
    return [
        validate_clean_required(item, max_length=item_max_length, field_name=field_name)
        for item in value
    ]


def _normalize_utc_datetime(value: datetime | str) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return as_utc(value)


UtcDatetime = Annotated[datetime, BeforeValidator(_normalize_utc_datetime)]
