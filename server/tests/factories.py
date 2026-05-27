from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.core.utils import generate_short_code
from app.models.feedback import Feedback
from app.models.google_auth import GoogleCredential
from app.models.google_sync_queue import GoogleSyncQueue, SyncAction, SyncStatus
from app.models.task import Task, TaskStatus
from app.models.url import ShortenedUrl
from app.models.user import User


async def create_user(
    db: AsyncSession,
    email: str = "test@glorng.dev",
    password: str = "testpass123",
    is_verified: bool = True,
    is_admin: bool = False,
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_verified=is_verified,
        is_admin=is_admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_short_url(
    db: AsyncSession,
    original_url: str = "https://example.com",
    created_by: int = 1,
    title: str | None = None,
) -> ShortenedUrl:
    url = ShortenedUrl(
        code=generate_short_code(8),
        original_url=original_url,
        title=title,
        created_by=created_by,
    )
    db.add(url)
    await db.commit()
    await db.refresh(url)
    return url


async def create_task(
    db: AsyncSession,
    telegram_user_id: int = 123456,
    title: str = "Test task",
    scheduled_at: str = "2026-06-01T12:00:00",
    description: str | None = None,
    location: str | None = None,
    status: TaskStatus = TaskStatus.PENDING,
    google_event_id: str | None = None,
) -> Task:
    task = Task(
        telegram_user_id=telegram_user_id,
        title=title,
        scheduled_at=scheduled_at,
        description=description,
        location=location,
        status=status,
        google_event_id=google_event_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def create_google_credential(
    db: AsyncSession,
    telegram_user_id: int = 123456,
    refresh_token: str = "fake-refresh-token",
    calendar_id: str = "primary",
) -> GoogleCredential:
    cred = GoogleCredential(
        telegram_user_id=telegram_user_id,
        refresh_token=refresh_token,
        calendar_id=calendar_id,
    )
    db.add(cred)
    await db.commit()
    await db.refresh(cred)
    return cred


async def create_sync_queue_item(
    db: AsyncSession,
    task_id: int,
    action: SyncAction = SyncAction.CREATE,
    status: SyncStatus = SyncStatus.PENDING,
    google_event_id: str | None = None,
    attempts: int = 0,
) -> GoogleSyncQueue:
    item = GoogleSyncQueue(
        task_id=task_id,
        action=action,
        status=status,
        google_event_id=google_event_id,
        attempts=attempts,
        next_retry_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def create_feedback(
    db: AsyncSession,
    email: str = "visitor@example.com",
    theme: str = "Bug report",
    message: str = "Found a bug on the home page.",
    status: str = "unread",
) -> Feedback:
    entry = Feedback(email=email, theme=theme, message=message, status=status)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry
