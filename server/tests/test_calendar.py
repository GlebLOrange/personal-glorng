"""Tests for Google Calendar integration: sync service, queue, callback, worker."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import calendar_datetime
from app.db.models.google_sync_queue import SyncAction, SyncStatus
from app.services.calendar import _build_event_body, sync_task_to_google
from app.services.task import enqueue_calendar_sync
from app.workers.tasks import process_sync_queue
from tests.factories import (
    create_google_credential,
    create_sync_queue_item,
    create_task,
)


def _session_ctx(
    db: AsyncSession,
) -> callable:
    """Build a fake session factory that yields the test db session."""

    @asynccontextmanager
    async def _ctx() -> AsyncGenerator[AsyncSession, None]:
        yield db

    return _ctx


# --- _build_event_body ---


class TestBuildEventBody:
    async def test_minimal_fields(self, db: AsyncSession) -> None:
        task = await create_task(db, title="Dentist")
        body = _build_event_body(task)

        assert body["summary"] == "Dentist"
        assert "description" not in body
        assert "location" not in body

    async def test_all_fields(self, db: AsyncSession) -> None:
        task = await create_task(
            db,
            title="Meeting",
            description="Discuss roadmap",
            location="Office",
        )
        body = _build_event_body(task)

        assert body["summary"] == "Meeting"
        assert body["description"] == "Discuss roadmap"
        assert body["location"] == "Office"
        expected = calendar_datetime(task.scheduled_at)
        assert body["start"]["dateTime"] == expected
        assert body["end"]["dateTime"] == expected


# --- enqueue_calendar_sync ---


class TestEnqueueCalendarSync:
    async def test_creates_pending_entry(self, db: AsyncSession) -> None:
        task = await create_task(db)
        entry = await enqueue_calendar_sync(
            db, task_id=task.id, action=SyncAction.CREATE
        )
        await db.commit()

        assert entry.task_id == task.id
        assert entry.action == SyncAction.CREATE
        assert entry.status == SyncStatus.PENDING
        assert entry.next_retry_at is not None

    async def test_preserves_google_event_id(self, db: AsyncSession) -> None:
        task = await create_task(db)
        entry = await enqueue_calendar_sync(
            db,
            task_id=task.id,
            action=SyncAction.DELETE,
            google_event_id="evt_abc",
        )
        await db.commit()

        assert entry.google_event_id == "evt_abc"
        assert entry.action == SyncAction.DELETE


# --- sync_task_to_google ---


class TestSyncTaskToGoogle:
    @patch("app.services.calendar._build_service")
    async def test_create_sets_event_id(
        self, mock_service_fn: MagicMock, db: AsyncSession
    ) -> None:
        task = await create_task(db)
        await create_google_credential(db, telegram_user_id=task.telegram_user_id)
        item = await create_sync_queue_item(
            db, task_id=task.id, action=SyncAction.CREATE
        )

        mock_service = MagicMock()
        mock_service.events().insert().execute.return_value = {"id": "gcal_123"}
        mock_service_fn.return_value = mock_service

        await sync_task_to_google(db, item)
        await db.commit()

        await db.refresh(task)
        assert task.google_event_id == "gcal_123"

    @patch("app.services.calendar._build_service")
    async def test_update_calls_api(
        self, mock_service_fn: MagicMock, db: AsyncSession
    ) -> None:
        task = await create_task(db, google_event_id="gcal_existing")
        await create_google_credential(db, telegram_user_id=task.telegram_user_id)
        item = await create_sync_queue_item(
            db, task_id=task.id, action=SyncAction.UPDATE
        )

        mock_service = MagicMock()
        mock_service_fn.return_value = mock_service

        await sync_task_to_google(db, item)

        mock_service.events().update.assert_called_once()

    @patch("app.services.calendar._build_service")
    async def test_delete_calls_api(
        self, mock_service_fn: MagicMock, db: AsyncSession
    ) -> None:
        task = await create_task(db, google_event_id="gcal_to_delete")
        await create_google_credential(db, telegram_user_id=task.telegram_user_id)
        item = await create_sync_queue_item(
            db, task_id=task.id, action=SyncAction.DELETE
        )

        mock_service = MagicMock()
        mock_service_fn.return_value = mock_service

        await sync_task_to_google(db, item)

        mock_service.events().delete.assert_called_once()

    async def test_skips_when_no_credentials(self, db: AsyncSession) -> None:
        task = await create_task(db, telegram_user_id=999999)
        item = await create_sync_queue_item(
            db, task_id=task.id, action=SyncAction.CREATE
        )

        await sync_task_to_google(db, item)
        await db.refresh(task)
        assert task.google_event_id is None

    async def test_skips_when_task_deleted(self, db: AsyncSession) -> None:
        task = await create_task(db)
        item = await create_sync_queue_item(
            db, task_id=task.id, action=SyncAction.CREATE
        )
        await db.delete(task)
        await db.commit()

        await sync_task_to_google(db, item)


# --- process_sync_queue ---


class TestProcessSyncQueue:
    @patch("app.services.calendar._build_service")
    @patch("app.workers.tasks.get_session_factory")
    async def test_processes_pending_items(
        self,
        mock_factory: MagicMock,
        mock_service_fn: MagicMock,
        db: AsyncSession,
    ) -> None:
        task = await create_task(db)
        await create_google_credential(db, telegram_user_id=task.telegram_user_id)
        item = await create_sync_queue_item(
            db, task_id=task.id, action=SyncAction.CREATE
        )

        mock_service = MagicMock()
        mock_service.events().insert().execute.return_value = {"id": "gcal_worker"}
        mock_service_fn.return_value = mock_service
        mock_factory.return_value = _session_ctx(db)

        await process_sync_queue({})

        await db.refresh(item)
        assert item.status == SyncStatus.COMPLETED

    @patch("app.services.calendar._build_service")
    @patch("app.workers.tasks.get_session_factory")
    async def test_retries_on_failure(
        self,
        mock_factory: MagicMock,
        mock_service_fn: MagicMock,
        db: AsyncSession,
    ) -> None:
        task = await create_task(db)
        await create_google_credential(db, telegram_user_id=task.telegram_user_id)
        item = await create_sync_queue_item(
            db, task_id=task.id, action=SyncAction.CREATE
        )

        mock_service = MagicMock()
        mock_service.events().insert().execute.side_effect = RuntimeError("API down")
        mock_service_fn.return_value = mock_service
        mock_factory.return_value = _session_ctx(db)

        await process_sync_queue({})

        await db.refresh(item)
        assert item.status == SyncStatus.PENDING
        assert item.attempts == 1
        assert "API down" in item.last_error

    @patch("app.services.calendar._build_service")
    @patch("app.workers.tasks.get_session_factory")
    async def test_marks_failed_after_max_attempts(
        self,
        mock_factory: MagicMock,
        mock_service_fn: MagicMock,
        db: AsyncSession,
    ) -> None:
        task = await create_task(db)
        await create_google_credential(db, telegram_user_id=task.telegram_user_id)
        item = await create_sync_queue_item(
            db,
            task_id=task.id,
            action=SyncAction.CREATE,
            attempts=4,
        )

        mock_service = MagicMock()
        mock_service.events().insert().execute.side_effect = RuntimeError(
            "still broken"
        )
        mock_service_fn.return_value = mock_service
        mock_factory.return_value = _session_ctx(db)

        await process_sync_queue({})

        await db.refresh(item)
        assert item.status == SyncStatus.FAILED
        assert item.attempts == 5

    @patch("app.workers.tasks.get_session_factory")
    async def test_skips_future_retry_items(
        self,
        mock_factory: MagicMock,
        db: AsyncSession,
    ) -> None:
        task = await create_task(db)
        item = await create_sync_queue_item(
            db, task_id=task.id, action=SyncAction.CREATE
        )
        item.next_retry_at = datetime.now(UTC) + timedelta(hours=1)
        db.add(item)
        await db.commit()

        mock_factory.return_value = _session_ctx(db)

        await process_sync_queue({})

        await db.refresh(item)
        assert item.status == SyncStatus.PENDING


# --- OAuth callback ---


class TestGoogleOAuthCallback:
    @patch("app.routers.callbacks.Flow")
    @patch("app.routers.callbacks.Bot")
    async def test_stores_credential(
        self,
        mock_bot_cls: MagicMock,
        mock_flow_cls: MagicMock,
        client: AsyncClient,
    ) -> None:
        mock_creds = MagicMock()
        mock_creds.refresh_token = "new-refresh-token"

        mock_flow = MagicMock()
        mock_flow.credentials = mock_creds
        mock_flow_cls.from_client_config.return_value = mock_flow

        mock_bot = AsyncMock()
        mock_bot_cls.return_value = mock_bot

        resp = await client.get(
            "/api/callbacks/google",
            params={"code": "auth-code", "state": "123456"},
        )

        assert resp.status_code == 200
        assert "Connected" in resp.text

    @patch("app.routers.callbacks.Flow")
    async def test_rejects_missing_refresh_token(
        self,
        mock_flow_cls: MagicMock,
        client: AsyncClient,
    ) -> None:
        mock_creds = MagicMock()
        mock_creds.refresh_token = None

        mock_flow = MagicMock()
        mock_flow.credentials = mock_creds
        mock_flow_cls.from_client_config.return_value = mock_flow

        resp = await client.get(
            "/api/callbacks/google",
            params={"code": "auth-code", "state": "123456"},
        )

        assert resp.status_code == 400

    async def test_rejects_invalid_state(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/callbacks/google",
            params={"code": "auth-code", "state": "not-a-number"},
        )

        assert resp.status_code == 400
