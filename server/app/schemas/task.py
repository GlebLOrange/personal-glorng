from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.text import sanitize_optional_text, sanitize_text
from app.db.models.task import TaskStatus
from app.schemas.validators import UtcDatetime


class TaskTextFields(BaseModel):
    """Shared task text sanitization for API schemas and service callers."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    location: str | None = Field(None, max_length=255)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        cleaned = sanitize_text(value, max_length=255)
        if not cleaned:
            msg = "Title must not be empty"
            raise ValueError(msg)
        return cleaned

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        return sanitize_optional_text(value)

    @field_validator("location")
    @classmethod
    def clean_location(cls, value: str | None) -> str | None:
        return sanitize_optional_text(value, max_length=255)


class TaskCreate(TaskTextFields):
    scheduled_at: UtcDatetime = Field(
        description="Task start time (ISO 8601). Naive values are treated as UTC.",
    )
    telegram_user_id: int | None = None
    reminder_minutes: int | None = Field(None, ge=1, le=1440)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskReschedule(BaseModel):
    scheduled_at: UtcDatetime = Field(
        description="New task start time (ISO 8601). Naive values are treated as UTC.",
    )


class TaskReminderCreate(BaseModel):
    minutes_before: int = Field(ge=1, le=1440)


class TaskResponse(BaseModel):
    id: int
    telegram_user_id: int
    title: str
    description: str | None
    location: str | None
    scheduled_at: datetime
    status: str
    google_event_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReminderResponse(BaseModel):
    id: int
    task_id: int
    remind_at: datetime
    sent: bool
    arq_job_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatusHistoryResponse(BaseModel):
    id: int
    task_id: int
    old_status: str
    new_status: str
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyncQueueResponse(BaseModel):
    id: int
    task_id: int
    action: str
    attempts: int
    last_error: str | None
    next_retry_at: datetime | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskDetailResponse(TaskResponse):
    reminders: list[ReminderResponse] = []
    status_history: list[StatusHistoryResponse] = []


class TaskStatsResponse(BaseModel):
    pending: int
    completed: int
    total: int
    failed_syncs: int
