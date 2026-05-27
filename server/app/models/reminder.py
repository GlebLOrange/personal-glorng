from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModelMixin


class Reminder(BaseModelMixin, Base):
    __tablename__ = "reminders"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True,
    )
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sent: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    arq_job_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    task: Mapped["Task"] = relationship(lazy="selectin")  # noqa: F821
