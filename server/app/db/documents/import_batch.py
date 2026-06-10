"""Import batch metadata documents."""

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.db.documents.base import TimestampedDocument

ImportBatchStatus = Literal["completed", "partial", "failed"]


class ImportBatch(TimestampedDocument):
    filename: str
    format: str
    profile: str | None = None
    status: ImportBatchStatus
    row_count: int
    error_count: int
    imported_by: int
    promoted_count: int = 0
    promoted_at: datetime | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
