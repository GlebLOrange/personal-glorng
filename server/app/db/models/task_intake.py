import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IntakeStatus(enum.StrEnum):
    PARSING = "parsing"
    CLARIFYING = "clarifying"
    READY = "ready"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class TaskIntake(Base):
    __tablename__ = "task_intakes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inbound_message_id: Mapped[int] = mapped_column(
        ForeignKey("telegram_inbound_messages.id", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[IntakeStatus] = mapped_column(
        Enum(
            IntakeStatus,
            name="intake_status",
            values_callable=lambda e: [x.value for x in e],
        ),
        default=IntakeStatus.PARSING,
        server_default="parsing",
    )
    draft_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    clarification_turns_json: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        server_default="[]",
    )
    clarification_rounds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
