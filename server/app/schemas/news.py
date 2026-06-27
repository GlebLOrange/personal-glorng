"""Pydantic schemas for curated news APIs."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.db.documents.news import NewsStatus
from app.schemas.common import PaginatedResponse
from app.schemas.validators import (
    validate_clean_optional,
    validate_clean_required,
    validate_clean_string_list,
)

NewsTheme = Literal[
    "world",
    "business",
    "tech",
    "security",
    "climate",
    "science",
    "health",
    "culture",
    "politics",
]

ALLOWED_NEWS_THEMES: set[str] = set(NewsTheme.__args__)


class NewsArticleCreate(BaseModel):
    """Admin/create payload for curated news articles."""

    source_name: str = Field(min_length=1, max_length=120)
    source_url: HttpUrl
    source_feed_url: HttpUrl
    source_published_at: datetime | None = None
    original_title: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=90)
    summary: str = Field(min_length=1, max_length=600)
    bullets: list[str] = Field(min_length=2, max_length=5)
    themes: list[NewsTheme] = Field(min_length=1, max_length=4)
    language: str = Field(default="en", min_length=2, max_length=12)
    status: NewsStatus = "draft"
    ai_model: str | None = Field(None, max_length=120)
    ai_input_hash: str | None = Field(None, max_length=128)
    ingest_error: str | None = Field(None, max_length=500)

    @field_validator("source_name", "original_title", "title")
    @classmethod
    def clean_required_short(cls, value: str) -> str:
        """Sanitize required short text fields."""
        return validate_clean_required(value, max_length=255)

    @field_validator("summary")
    @classmethod
    def clean_summary(cls, value: str) -> str:
        """Sanitize article summary."""
        return validate_clean_required(value, max_length=600, field_name="Summary")

    @field_validator("bullets")
    @classmethod
    def clean_bullets(cls, value: list[str]) -> list[str]:
        """Sanitize bullet points."""
        return validate_clean_string_list(
            value,
            item_max_length=180,
            field_name="Bullet",
        )

    @field_validator("language")
    @classmethod
    def clean_language(cls, value: str) -> str:
        """Normalize language code."""
        cleaned = validate_clean_required(
            value,
            max_length=12,
            field_name="Language",
        )
        return cleaned.lower()

    @field_validator("ai_model", "ai_input_hash", "ingest_error")
    @classmethod
    def clean_optional_meta(cls, value: str | None) -> str | None:
        """Sanitize optional metadata fields."""
        return validate_clean_optional(value, max_length=500)


class NewsArticleUpdate(BaseModel):
    """Admin update payload for curated news articles."""

    status: NewsStatus | None = None
    source_name: str | None = Field(None, min_length=1, max_length=120)
    source_url: HttpUrl | None = None
    source_feed_url: HttpUrl | None = None
    source_published_at: datetime | None = None
    original_title: str | None = Field(None, min_length=1, max_length=255)
    title: str | None = Field(None, min_length=1, max_length=90)
    summary: str | None = Field(None, min_length=1, max_length=600)
    bullets: list[str] | None = Field(None, min_length=2, max_length=5)
    themes: list[NewsTheme] | None = Field(None, min_length=1, max_length=4)
    language: str | None = Field(None, min_length=2, max_length=12)
    ingest_error: str | None = Field(None, max_length=500)

    @field_validator("source_name", "original_title", "title")
    @classmethod
    def clean_required_short(cls, value: str | None) -> str | None:
        """Sanitize optional short text fields."""
        if value is None:
            return None
        return validate_clean_required(value, max_length=255)

    @field_validator("summary")
    @classmethod
    def clean_summary(cls, value: str | None) -> str | None:
        """Sanitize optional summary."""
        if value is None:
            return None
        return validate_clean_required(value, max_length=600, field_name="Summary")

    @field_validator("bullets")
    @classmethod
    def clean_bullets(cls, value: list[str] | None) -> list[str] | None:
        """Sanitize optional bullet points."""
        if value is None:
            return None
        return validate_clean_string_list(
            value,
            item_max_length=180,
            field_name="Bullet",
        )

    @field_validator("language")
    @classmethod
    def clean_language(cls, value: str | None) -> str | None:
        """Normalize optional language code."""
        if value is None:
            return None
        cleaned = validate_clean_required(
            value,
            max_length=12,
            field_name="Language",
        )
        return cleaned.lower()

    @field_validator("ingest_error")
    @classmethod
    def clean_ingest_error(cls, value: str | None) -> str | None:
        """Sanitize optional ingest error."""
        return validate_clean_optional(value, max_length=500)


class NewsArticleResponse(BaseModel):
    """Curated news article response."""

    id: int
    slug: str
    status: NewsStatus
    source_name: str
    source_url: str
    source_feed_url: str
    source_published_at: datetime | None
    original_title: str
    title: str
    summary: str
    bullets: list[str]
    themes: list[str]
    language: str
    published_at: datetime | None
    telegram_message_id: int | None
    ai_model: str | None
    ingest_error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NewsArticleListResponse(PaginatedResponse[NewsArticleResponse]):
    """Paginated news article list response."""


class NewsIngestResponse(BaseModel):
    """Result of a news ingestion run."""

    processed: int
    created: int
    skipped: int
    failed: int
