import enum

from sqlalchemy import Index, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BaseModelMixin
from app.db.search_index import SEARCH_FTS_EXPRESSION, SEARCH_INDEX_NAME


class SearchVisibility(enum.StrEnum):
    PUBLIC = "public"
    ADMIN = "admin"


class SearchDocument(BaseModelMixin, Base):
    __tablename__ = "search_documents"
    __table_args__ = (
        UniqueConstraint("source_type", "source_id", name="uq_search_documents_source"),
        Index(
            SEARCH_INDEX_NAME,
            text(SEARCH_FTS_EXPRESSION),
            postgresql_using="gin",
        ),
    )

    source_type: Mapped[str] = mapped_column(String(32), index=True)
    source_id: Mapped[int] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(512), server_default="/")
    visibility: Mapped[str] = mapped_column(
        String(16),
        server_default=SearchVisibility.PUBLIC,
        index=True,
    )
