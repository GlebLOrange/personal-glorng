"""Google Calendar sync service."""

import asyncio

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.logging import logger
from app.core.utils import as_utc, calendar_datetime
from app.db.documents.credential import GoogleCredential
from app.db.documents.task import GoogleSyncQueue, SyncAction, Task
from app.db.registry import DatabaseRegistry
from app.services.google_credentials import read_google_refresh_token
from app.settings import get_settings


def _build_service(cred: GoogleCredential) -> object:
    """Authenticate and return a Google Calendar API service."""
    settings = get_settings()
    credentials = Credentials(
        token=None,
        refresh_token=read_google_refresh_token(cred.refresh_token),
        token_uri="https://oauth2.googleapis.com/token",  # noqa: S106
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    )
    credentials.refresh(Request())
    return build("calendar", "v3", credentials=credentials)


def _build_event_body(
    task: Task,
    *,
    reminder_minutes: list[int] | None = None,
) -> dict[str, object]:
    """Build Google Calendar event body from task."""
    scheduled = calendar_datetime(task.scheduled_at)
    minutes = reminder_minutes if reminder_minutes is not None else []
    body: dict[str, object] = {
        "summary": task.title,
        "start": {"dateTime": scheduled, "timeZone": "UTC"},
        "end": {"dateTime": scheduled, "timeZone": "UTC"},
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": m} for m in minutes if m > 0
            ],
        },
    }
    if task.description:
        body["description"] = task.description
    if task.location:
        body["location"] = task.location
    return body


def _create_event_sync(
    cred: GoogleCredential,
    task: Task,
    reminder_minutes: list[int] | None = None,
) -> str:
    service = _build_service(cred)
    event = (
        service.events()
        .insert(
            calendarId=cred.calendar_id,
            body=_build_event_body(task, reminder_minutes=reminder_minutes),
        )
        .execute()
    )
    return event["id"]


def _update_event_sync(
    cred: GoogleCredential,
    task: Task,
    event_id: str,
    reminder_minutes: list[int] | None = None,
) -> None:
    service = _build_service(cred)
    service.events().update(
        calendarId=cred.calendar_id,
        eventId=event_id,
        body=_build_event_body(task, reminder_minutes=reminder_minutes),
    ).execute()


def _delete_event_sync(
    cred: GoogleCredential,
    event_id: str,
) -> None:
    service = _build_service(cred)
    service.events().delete(
        calendarId=cred.calendar_id,
        eventId=event_id,
    ).execute()


async def _reminder_minutes_for_task(
    registry: DatabaseRegistry,
    task: Task,
) -> list[int]:
    """Derive Google popup lead times from unsent Telegram reminders."""
    assert registry.tasks is not None
    reminders = await registry.tasks.list_reminders_for_task(task.id)
    scheduled = as_utc(task.scheduled_at)
    minutes: list[int] = []
    seen: set[int] = set()
    for rem in reminders:
        if rem.sent:
            continue
        delta_minutes = int((scheduled - as_utc(rem.remind_at)).total_seconds() // 60)
        if delta_minutes > 0 and delta_minutes not in seen:
            seen.add(delta_minutes)
            minutes.append(delta_minutes)
    return minutes


async def sync_task_to_google(
    registry: DatabaseRegistry,
    queue_item: GoogleSyncQueue,
) -> str | None:
    """Process a single sync queue item.

    Returns ``None`` on success, or a skip reason when the item cannot be
    synced yet (so the worker can mark it failed and allow admin retry).
    """
    if registry.tasks is None or registry.credentials is None:
        msg = "Task or credential repository is not initialized"
        raise RuntimeError(msg)

    task = await registry.tasks.get_or_none(queue_item.task_id)
    if not task:
        logger.warning(
            "Sync: task not found",
            context={"task_id": queue_item.task_id},
        )
        return "Task not found"

    cred = await registry.credentials.get_google_for_telegram_user(
        task.telegram_user_id,
    )
    if not cred:
        logger.info(
            "Sync: no Google credentials",
            context={"telegram_user_id": task.telegram_user_id},
        )
        return "No Google credentials"

    reminder_minutes = await _reminder_minutes_for_task(registry, task)

    if queue_item.action == SyncAction.CREATE:
        event_id = await asyncio.to_thread(
            _create_event_sync,
            cred,
            task,
            reminder_minutes,
        )
        await registry.tasks.update_fields(task.id, google_event_id=event_id)
        logger.info(
            "Calendar event created",
            context={"task_id": task.id, "event_id": event_id},
        )

    elif queue_item.action == SyncAction.UPDATE:
        event_id = queue_item.google_event_id or task.google_event_id
        if event_id:
            await asyncio.to_thread(
                _update_event_sync,
                cred,
                task,
                event_id,
                reminder_minutes,
            )
            logger.info(
                "Calendar event updated",
                context={"task_id": task.id, "event_id": event_id},
            )

    elif queue_item.action == SyncAction.DELETE:
        event_id = queue_item.google_event_id or task.google_event_id
        if event_id:
            await asyncio.to_thread(
                _delete_event_sync,
                cred,
                event_id,
            )
            logger.info(
                "Calendar event deleted",
                context={"task_id": task.id, "event_id": event_id},
            )

    return None
