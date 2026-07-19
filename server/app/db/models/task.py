import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BaseModelMixin


class TaskStatus(enum.StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    NOT_COMPLETED = "not_completed"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class Task(BaseModelMixin, Base):
    __tablename__ = "tasks"

    telegram_user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            name="task_status",
            values_callable=lambda e: [x.value for x in e],
        ),
        default=TaskStatus.NOT_COMPLETED,
        server_default="pending",
    )
    google_event_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    intake_id: Mapped[int | None] = mapped_column(
        ForeignKey("task_intakes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    jira_issue_key: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
