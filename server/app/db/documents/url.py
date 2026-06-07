from app.db.documents.base import TimestampedDocument


class ShortenedUrl(TimestampedDocument):
    code: str
    original_url: str
    title: str | None = None
    clicks: int = 0
    created_by: int | None = None
