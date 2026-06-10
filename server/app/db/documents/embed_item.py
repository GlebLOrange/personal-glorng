"""Promoted embed items from pipe-delimited import feeds."""

from typing import Any

from pydantic import Field

from app.db.documents.base import TimestampedDocument


class EmbedItem(TimestampedDocument):
    """Normalized embed metadata promoted from import staging."""

    embed_id: str
    embed_url: str | None = None
    title: str | None = None
    thumb_url: str | None = None
    thumb_base_url: str | None = None
    preview_urls: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    performers: list[str] = Field(default_factory=list)
    channel: str | None = None
    duration_sec: int | None = None
    view_count: int | None = None
    upvote_count: int | None = None
    downvote_count: int | None = None
    rating_percent: float | None = None
    source_batch_id: int
    source_row_id: int
    raw_fields: dict[str, Any] = Field(default_factory=dict)
