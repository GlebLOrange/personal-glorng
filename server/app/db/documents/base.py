"""Base document types for MongoDB-backed domain models."""

from datetime import UTC, date, datetime
from decimal import Decimal
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


def _mongo_value(value: Any) -> Any:
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, datetime.min.time(), tzinfo=UTC)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: _mongo_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_mongo_value(item) for item in value]
    return value


def document_to_dict(doc: BaseModel, *, exclude_none: bool = False) -> dict[str, Any]:
    """Serialize a document for MongoDB/BSON storage."""
    raw = doc.model_dump(mode="python", exclude_none=exclude_none)
    return {key: _mongo_value(value) for key, value in raw.items()}
