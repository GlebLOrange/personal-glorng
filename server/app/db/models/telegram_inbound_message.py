from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TelegramInboundMessage(Base):
    __tablename__ = "telegram_inbound_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    telegram_message_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    chat_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
