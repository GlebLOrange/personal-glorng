import re
from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
)

from app.core.url_safety import validate_redirect_url
from app.schemas.common import PaginatedResponse
from app.schemas.validators import validate_clean_optional

_HAS_AUTHORITY_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)


def _ensure_http_scheme(value: object) -> object:
    """Prepend https:// when there is no scheme (does not invent www)."""
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
    # Leave ftp:// etc. alone so HttpUrl / safety can reject them.
    if _HAS_AUTHORITY_SCHEME.match(trimmed):
        return trimmed
    return f"https://{trimmed}"


HttpRedirectUrl = Annotated[HttpUrl, BeforeValidator(_ensure_http_scheme)]


class UrlCreate(BaseModel):
    original_url: HttpRedirectUrl
    title: str | None = Field(None, max_length=255)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=255)

    @field_validator("original_url")
    @classmethod
    def validate_safe_url(cls, value: HttpUrl) -> HttpUrl:
        validate_redirect_url(str(value))
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_url": "https://example.com/very-long-url",
                "title": "Example Site",
            }
        }
    )


class UrlUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated title",
            }
        }
    )


class UrlResponse(BaseModel):
    id: int
    code: str
    original_url: str
    title: str | None
    clicks: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "code": "aBcD1234",
                "original_url": "https://example.com/very-long-url",
                "title": "Example Site",
                "clicks": 42,
                "created_at": "2026-05-25T03:00:00Z",
            }
        },
    )


class UrlListResponse(PaginatedResponse[UrlResponse]):
    """Paginated URL shortener list."""
