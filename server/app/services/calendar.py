"""Google Calendar sync service."""

import asyncio

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.utils import calendar_datetime
from app.db.models.google_auth import GoogleCredential
from app.db.models.google_sync_queue import GoogleSyncQueue, SyncAction
from app.db.models.task import Task
from app.settings import get_settings


def _build_service(cred: GoogleCredential) -> object:
    """Authenticate and return a Google Calendar API service."""
    settings = get_settings()
    credentials = Credentials(
        token=None,
        refresh_token=cred.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",  # noqa: S106
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    )
    credentials.refresh(Request())
    return build("calendar", "v3", credentials=credentials)


def _build_event_body(task: Task) -> dict[str, object]:
    """Build Google Calendar event body from task."""
    scheduled = calendar_datetime(task.scheduled_at)
    body: dict[str, object] = {
        "summary": task.title,
        "start": {"dateTime": scheduled, "timeZone": "UTC"},
        "end": {"dateTime": scheduled, "timeZone": "UTC"},
    }
    if task.description:
        body["description"] = task.description
    if task.location:
        body["location"] = task.location
    return body


def _create_event_sync(
    cred: GoogleCredential,
    task: Task,
) -> str:
    service = _build_service(cred)
    event = (
        service.events()
        .insert(calendarId=cred.calendar_id, body=_build_event_body(task))
        .execute()
    )
    return event["id"]


def _update_event_sync(
    cred: GoogleCredential,
    task: Task,
    event_id: str,
) -> None:
    service = _build_service(cred)
    service.events().update(
        calendarId=cred.calendar_id,
        eventId=event_id,
        body=_build_event_body(task),
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


async def sync_task_to_google(
    db: AsyncSession,
    queue_item: GoogleSyncQueue,
) -> None:
    """Process a single sync queue item."""
    result = await db.execute(
        select(Task).where(Task.id == queue_item.task_id),
    )
    task = result.scalar_one_or_none()
    if not task:
        logger.warning(
            "Sync: task not found",
            context={"task_id": queue_item.task_id},
        )
        return

    cred_result = await db.execute(
        select(GoogleCredential).where(
            GoogleCredential.telegram_user_id == task.telegram_user_id,
        ),
    )
    cred = cred_result.scalar_one_or_none()
    if not cred:
        logger.info(
            "Sync: no Google credentials",
            context={"telegram_user_id": task.telegram_user_id},
        )
        return

    if queue_item.action == SyncAction.CREATE:
        event_id = await asyncio.to_thread(
            _create_event_sync,
            cred,
            task,
        )
        task.google_event_id = event_id
        db.add(task)
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
