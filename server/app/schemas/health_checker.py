"""Pydantic schemas for the health-checker tool."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
)

from app.schemas.common import PaginatedResponse
from app.schemas.validators import validate_clean_optional

_HAS_AUTHORITY_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)

IntervalMinutes = Literal[1, 5, 15, 60]


def _ensure_http_scheme(value: object) -> object:
    """Prepend https:// when there is no scheme."""
    if not isinstance(value, str):
        return value
    trimmed = value.strip()
    if not trimmed:
        return trimmed
    lower = trimmed.lower()
    if lower.startswith(("http://", "https://")):
        return trimmed
    if trimmed.startswith("//"):
        return f"https:{trimmed}"
    if _HAS_AUTHORITY_SCHEME.match(trimmed):
        return trimmed
    return f"https://{trimmed}"


HttpMonitorUrl = Annotated[HttpUrl, BeforeValidator(_ensure_http_scheme)]


class DnsRecordResponse(BaseModel):
    family: str
    address: str

    model_config = ConfigDict(from_attributes=True)


class HealthMonitorCreate(BaseModel):
    url: HttpMonitorUrl
    label: str | None = Field(None, max_length=255)
    interval_minutes: IntervalMinutes = 5

    @field_validator("label")
    @classmethod
    def clean_label(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com",
                "label": "Example",
                "interval_minutes": 5,
            }
        }
    )


class HealthMonitorUpdate(BaseModel):
    label: str | None = Field(None, max_length=255)
    interval_minutes: IntervalMinutes | None = None
    enabled: bool | None = None

    @field_validator("label")
    @classmethod
    def clean_label(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "API prod",
                "interval_minutes": 15,
                "enabled": True,
            }
        }
    )


class HealthMonitorResponse(BaseModel):
    id: int
    url: str
    label: str | None
    interval_minutes: int
    enabled: bool
    next_check_at: datetime | None
    last_checked_at: datetime | None
    last_status_code: int | None
    last_response_ms: float | None
    last_ok: bool | None
    last_error: str | None
    uptime_percent: float | None
    ssl_expires_at: datetime | None
    dns: list[DnsRecordResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthMonitorListResponse(PaginatedResponse[HealthMonitorResponse]):
    """Paginated health monitor list."""


class HealthHistoryPoint(BaseModel):
    checked_at: datetime
    status_code: int | None
    response_ms: float | None
    ok: bool
    error: str | None = None

    model_config = ConfigDict(from_attributes=True)


class HealthHistoryResponse(BaseModel):
    items: list[HealthHistoryPoint]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "checked_at": "2026-09-23T12:00:00Z",
                        "status_code": 200,
                        "response_ms": 120.5,
                        "ok": True,
                        "error": None,
                    }
                ]
            }
        }
    )
