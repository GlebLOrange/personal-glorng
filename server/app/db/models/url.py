from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BaseModelMixin


class ShortenedUrl(BaseModelMixin, Base):
    __tablename__ = "shortened_urls"

    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    original_url: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    clicks: Mapped[int] = mapped_column(default=0)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
