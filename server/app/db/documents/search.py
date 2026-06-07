from enum import StrEnum

from app.db.documents.base import TimestampedDocument


class SearchVisibility(StrEnum):
    PUBLIC = "public"
    ADMIN = "admin"


class SearchDocument(TimestampedDocument):
    source_type: str
    source_id: int
    title: str
    body: str
    url: str = "/"
    visibility: str = SearchVisibility.PUBLIC
