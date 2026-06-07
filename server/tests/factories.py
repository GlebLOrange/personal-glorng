from datetime import UTC, datetime, timedelta

from app.core.utils import generate_short_code
from app.db.documents.credential import GoogleCredential
from app.db.documents.feedback import Feedback
from app.db.documents.task import (
    GoogleSyncQueue,
    SyncAction,
    SyncStatus,
    Task,
    TaskStatus,
)
from app.db.documents.url import ShortenedUrl
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.services.user import create_user as create_user_record
from app.services.user import default_owner_permissions


def _require(registry: DatabaseRegistry, attr: str):
    repo = getattr(registry, attr)
    if repo is None:
        msg = f"{attr} repository is not initialized"
        raise RuntimeError(msg)
    return repo


async def create_user(
    registry: DatabaseRegistry,
    email: str = "test@glorng.dev",
    password: str = "MyTestPass123!",
    is_verified: bool = True,
    is_protected: bool = False,
    permissions: list[str] | None = None,
) -> User:
    return await create_user_record(
        registry,
        email=email,
        password=password,
        is_verified=is_verified,
        is_protected=is_protected,
        permissions=permissions
        if permissions is not None
        else default_owner_permissions(),
    )


async def create_short_url(
    registry: DatabaseRegistry,
    original_url: str = "https://example.com",
    created_by: int | None = 1,
    title: str | None = None,
) -> ShortenedUrl:
    url = ShortenedUrl(
        code=generate_short_code(8),
        original_url=original_url,
        title=title,
        created_by=created_by,
    )
    return await _require(registry, "urls").insert(url)


async def create_task(
    registry: DatabaseRegistry,
    telegram_user_id: int = 123456,
    title: str = "Test task",
    scheduled_at: datetime | None = None,
    description: str | None = None,
    location: str | None = None,
    status: TaskStatus = TaskStatus.PENDING,
    google_event_id: str | None = None,
) -> Task:
    if scheduled_at is None:
        scheduled_at = datetime(2026, 6, 1, 12, 0, tzinfo=UTC)
    task = Task(
        telegram_user_id=telegram_user_id,
        title=title,
        scheduled_at=scheduled_at,
        description=description,
        location=location,
        status=status,
        google_event_id=google_event_id,
    )
    return await _require(registry, "tasks").insert(task)


async def create_google_credential(
    registry: DatabaseRegistry,
    telegram_user_id: int = 123456,
    refresh_token: str = "fake-refresh-token",
    calendar_id: str = "primary",
) -> GoogleCredential:
    cred = GoogleCredential(
        id=0,
        telegram_user_id=telegram_user_id,
        refresh_token=refresh_token,
        calendar_id=calendar_id,
    )
    return await _require(registry, "credentials").upsert_google(cred)


async def create_sync_queue_item(
    registry: DatabaseRegistry,
    task_id: int,
    action: SyncAction = SyncAction.CREATE,
    status: SyncStatus = SyncStatus.PENDING,
    google_event_id: str | None = None,
    attempts: int = 0,
) -> GoogleSyncQueue:
    item = GoogleSyncQueue(
        id=0,
        task_id=task_id,
        action=action,
        status=status,
        google_event_id=google_event_id,
        attempts=attempts,
        next_retry_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    return await _require(registry, "tasks").enqueue_sync(item)


async def create_feedback(
    registry: DatabaseRegistry,
    email: str = "visitor@example.com",
    theme: str = "Bug report",
    message: str = "Found a bug on the home page.",
    status: str = "unread",
) -> Feedback:
    entry = Feedback(email=email, theme=theme, message=message, status=status)
    return await _require(registry, "feedback").insert(entry)
