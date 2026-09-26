"""Schemas for the public QR code generator tool."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import PaginatedResponse
from app.schemas.validators import validate_clean_optional

QrErrorLevel = Literal["L", "M", "Q", "H"]
_CONTENT_PREVIEW_LEN = 80


class QrCodeCreate(BaseModel):
    """Request body for creating a QR code."""

    content: str = Field(..., min_length=1, max_length=2000)
    label: str | None = Field(None, max_length=120)
    error_level: QrErrorLevel = "M"

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            msg = "content must not be empty"
            raise ValueError(msg)
        return trimmed

    @field_validator("label")
    @classmethod
    def clean_label(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=120)


class QrCodeResponse(BaseModel):
    """QR metadata returned from create/list/get."""

    id: int
    content_preview: str
    label: str | None
    error_level: QrErrorLevel
    svg_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QrCodeListResponse(PaginatedResponse[QrCodeResponse]):
    """Paginated list of recently created QR codes."""


def content_preview(content: str) -> str:
    """Truncate stored content for public list responses."""
    if len(content) <= _CONTENT_PREVIEW_LEN:
        return content
    return f"{content[: _CONTENT_PREVIEW_LEN - 1]}…"
