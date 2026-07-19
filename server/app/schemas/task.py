from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.db.documents.task import TaskStatus
from app.schemas.common import PaginatedResponse
from app.schemas.validators import (
    UtcDatetime,
    validate_clean_optional,
    validate_clean_required,
)


class TaskTextFields(BaseModel):
    """Shared task text sanitization for API schemas and service callers."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    location: str | None = Field(None, max_length=255)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return validate_clean_required(value, max_length=255, field_name="Title")

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        return validate_clean_optional(value)

    @field_validator("location")
    @classmethod
    def clean_location(cls, value: str | None) -> str | None:
        return validate_clean_optional(value, max_length=255)


class TaskCreate(TaskTextFields):
    scheduled_at: UtcDatetime = Field(
        description="Task start time (ISO 8601). Naive values are treated as UTC.",
    )
    telegram_user_id: int | None = None
    reminder_minutes: int | None = Field(None, ge=1, le=1440)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Team standup",
                "description": "Daily sync",
                "location": "Zoom",
                "scheduled_at": "2026-06-09T09:00:00Z",
                "reminder_minutes": 15,
            }
        }
    )


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
    job_id: str | None
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
    task_title: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TaskDetailResponse(TaskResponse):
    reminders: list[ReminderResponse] = []
    status_history: list[StatusHistoryResponse] = []


class TaskStatsResponse(BaseModel):
    pending: int
    completed: int
    total: int
    failed_syncs: int


class TaskListResponse(PaginatedResponse[TaskResponse]):
    """Paginated task list."""


class SyncQueueListResponse(PaginatedResponse[SyncQueueResponse]):
    """Paginated calendar sync queue."""
