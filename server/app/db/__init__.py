"""Database package: MongoDB primary via registry; Postgres optional for secondary."""

from app.db.base import Base, BaseModelMixin
from app.db.models.audit_event import AuditEvent
from app.db.models.search_document import SearchDocument
from app.db.registry import DatabaseRegistry

__all__ = [
    "AuditEvent",
    "Base",
    "BaseModelMixin",
    "DatabaseRegistry",
    "SearchDocument",
]
