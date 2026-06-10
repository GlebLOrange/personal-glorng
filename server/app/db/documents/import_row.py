"""Staged import row documents."""

from typing import Any

from pydantic import Field

from app.db.documents.base import TimestampedDocument


class ImportRow(TimestampedDocument):
    batch_id: int
    row_index: int
    fields: dict[str, Any] = Field(default_factory=dict)
    raw_line: str | None = None
    error: str | None = None
