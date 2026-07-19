from datetime import datetime
from enum import StrEnum

from app.db.documents.base import TimestampedDocument, utc_now


class TaskStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    NOT_COMPLETED = "not_completed"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class IntakeStatus(StrEnum):
    PARSING = "parsing"
    CLARIFYING = "clarifying"
    READY = "ready"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class SyncAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class SyncStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(TimestampedDocument):
    telegram_user_id: int
    title: str
    description: str | None = None
    location: str | None = None
    scheduled_at: datetime
    status: TaskStatus = TaskStatus.NOT_COMPLETED
    google_event_id: str | None = None
    intake_id: int | None = None
    jira_issue_key: str | None = None


class TaskStatusHistory:
    def __init__(
        self,
        *,
        id: int,
        task_id: int,
        old_status: str,
        new_status: str,
        changed_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.task_id = task_id
        self.old_status = old_status
        self.new_status = new_status
        self.changed_at = changed_at or utc_now()


class Reminder(TimestampedDocument):
    task_id: int
    remind_at: datetime
    sent: bool = False
    job_id: str | None = None


class TaskIntake:
    def __init__(
        self,
        *,
        id: int,
        inbound_message_id: int,
        status: IntakeStatus = IntakeStatus.PARSING,
        draft_json: dict | None = None,
        confidence_json: dict | None = None,
        clarification_turns_json: list | None = None,
        clarification_rounds: int = 0,
        task_id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.inbound_message_id = inbound_message_id
        self.status = status
        self.draft_json = draft_json
        self.confidence_json = confidence_json
        self.clarification_turns_json = clarification_turns_json
        self.clarification_rounds = clarification_rounds
        self.task_id = task_id
        self.created_at = created_at or utc_now()
        self.updated_at = updated_at or utc_now()


class GoogleSyncQueue:
    def __init__(
        self,
        *,
        id: int,
        task_id: int,
        action: SyncAction,
        attempts: int = 0,
        last_error: str | None = None,
        next_retry_at: datetime | None = None,
        status: SyncStatus = SyncStatus.PENDING,
        created_at: datetime | None = None,
        error_notified: bool = False,
        google_event_id: str | None = None,
    ) -> None:
        self.id = id
        self.task_id = task_id
        self.action = action
        self.attempts = attempts
        self.last_error = last_error
        self.next_retry_at = next_retry_at
        self.status = status
        self.created_at = created_at or utc_now()
        self.error_notified = error_notified
        self.google_event_id = google_event_id
