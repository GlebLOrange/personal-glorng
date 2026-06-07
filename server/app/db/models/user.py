import uuid

from sqlalchemy import JSON, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BaseModelMixin


class User(BaseModelMixin, Base):
    __tablename__ = "users"

    public_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_protected: Mapped[bool] = mapped_column(default=False, server_default="false")
    permissions: Mapped[list[str]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        nullable=False,
    )
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(
        String(64), default="UTC", server_default="UTC"
    )
    preferences: Mapped[dict[str, object]] = mapped_column(
        JSON,
        server_default=text("'{}'::json"),
        nullable=False,
    )
