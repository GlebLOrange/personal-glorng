from datetime import datetime

from app.db.documents.base import TimestampedDocument


class NewsSource(TimestampedDocument):
    """Admin-managed RSS or Atom source for the public news page."""

    name: str
    feed_url: str
    category: str = "world"
    region: str = "global"
    enabled: bool = True
    last_error: str | None = None
    last_fetched_at: datetime | None = None


class NewsArticle(TimestampedDocument):
    """Stored news article for the public news page."""

    title: str
    link: str
    source: str = "gLOrng"
    origin: str = "manual"
    status: str = "published"
    category: str = "world"
    region: str = "global"
    summary: str | None = None
    published_at: datetime
    enabled: bool = True
