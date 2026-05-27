import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SyncAction(enum.StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class SyncStatus(enum.StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class GoogleSyncQueue(Base):
    __tablename__ = "google_sync_queue"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True,
    )
    action: Mapped[SyncAction] = mapped_column(
        Enum(
            SyncAction,
            name="sync_action",
            values_callable=lambda e: [x.value for x in e],
        ),
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[SyncStatus] = mapped_column(
        Enum(
            SyncStatus,
            name="sync_status",
            values_callable=lambda e: [x.value for x in e],
        ),
        default=SyncStatus.PENDING,
        server_default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    error_notified: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )

    google_event_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
