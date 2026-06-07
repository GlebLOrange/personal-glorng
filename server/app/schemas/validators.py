"""Reusable Pydantic field validators."""

from datetime import datetime
from typing import Annotated

from pydantic import BeforeValidator

from app.core.utils import as_utc


def _normalize_utc_datetime(value: datetime | str) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return as_utc(value)


UtcDatetime = Annotated[datetime, BeforeValidator(_normalize_utc_datetime)]
