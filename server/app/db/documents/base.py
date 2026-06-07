"""Base document types for MongoDB-backed domain models."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class TimestampedDocument(BaseModel):
    """Common fields shared by most persisted documents."""

    model_config = ConfigDict(from_attributes=True)

    id: int = 0
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


def document_to_dict(doc: BaseModel, *, exclude_none: bool = False) -> dict[str, Any]:
    """Serialize a document for MongoDB storage."""
    return doc.model_dump(mode="python", exclude_none=exclude_none)
