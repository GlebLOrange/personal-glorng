"""Schemas for the public QR code generator tool (ephemeral, no persistence)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import validate_clean_optional

QrErrorLevel = Literal["L", "M", "Q", "H"]
_CONTENT_PREVIEW_LEN = 80


class QrCodeCreate(BaseModel):
    """Request body for generating a QR code."""

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


class QrCodeGenerateResponse(BaseModel):
    """Inline SVG and metadata — nothing is stored server-side."""

    content_preview: str
    label: str | None
    error_level: QrErrorLevel
    svg: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content_preview": "https://example.com",
                "label": None,
                "error_level": "M",
                "svg": "<svg xmlns='http://www.w3.org/2000/svg' …></svg>",
            }
        }
    )


def content_preview(content: str) -> str:
    """Truncate payload for client display (full payload is only in the QR matrix)."""
    if len(content) <= _CONTENT_PREVIEW_LEN:
        return content
    return f"{content[: _CONTENT_PREVIEW_LEN - 1]}…"
