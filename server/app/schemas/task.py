from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.utils import as_utc


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    scheduled_at: datetime = Field(
        description="Task start time (ISO 8601). Naive values are treated as UTC.",
    )

    @field_validator("scheduled_at")
    @classmethod
    def normalize_scheduled_at(cls, value: datetime) -> datetime:
        return as_utc(value)
    description: str | None = None
    location: str | None = Field(None, max_length=255)
    telegram_user_id: int | None = None


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
