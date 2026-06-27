"""MongoDB document for curated news articles."""

from datetime import datetime
from typing import Literal

from app.db.documents.base import TimestampedDocument

NewsStatus = Literal["draft", "published", "unpublished", "failed"]


class NewsArticle(TimestampedDocument):
    """Persisted curated news article."""

    slug: str
    status: NewsStatus = "draft"
    source_id: int | None = None
    source_name: str
    source_url: str
    source_feed_url: str
    source_published_at: datetime | None = None
    original_title: str
    title: str
    summary: str
    bullets: str = "[]"
    themes: str = "[]"
    language: str = "en"
    published_at: datetime | None = None
    telegram_message_id: int | None = None
    ai_model: str | None = None
    ai_input_hash: str | None = None
    ingest_error: str | None = None


class NewsSource(TimestampedDocument):
    """Persisted RSS/Atom source for news ingestion."""

    name: str
    feed_url: str
    host: str | None = None
    category: str = "world"
    region: str = "global"
    enabled: bool = True
    last_error: str | None = None
    last_fetched_at: datetime | None = None
