from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BaseModelMixin


class Feedback(BaseModelMixin, Base):
    __tablename__ = "feedback"

    email: Mapped[str] = mapped_column(String(255))
    theme: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="unread")
