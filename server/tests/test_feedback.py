from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.db.registry import DatabaseRegistry
from tests.factories import create_feedback


@pytest.fixture
def mock_notify():
    with patch("app.routers.feedback.notify_admin", new_callable=AsyncMock) as m:
        yield m


class TestCreateFeedback:
    async def test_create_feedback(self, client: AsyncClient, mock_notify: AsyncMock):
        resp = await client.post(
            "/api/feedback",
            json={
                "email": "test@example.com",
                "theme": "Hello",
                "message": "Great site!",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert data["theme"] == "Hello"
        assert data["status"] == "unread"
        mock_notify.assert_called_once()

    async def test_create_feedback_invalid_email(self, client: AsyncClient):
        resp = await client.post(
            "/api/feedback",
            json={
                "email": "not-an-email",
                "theme": "Test",
                "message": "Body",
            },
        )
        assert resp.status_code == 422

    async def test_create_feedback_empty_theme(self, client: AsyncClient):
        resp = await client.post(
            "/api/feedback",
            json={
                "email": "test@example.com",
                "theme": "",
                "message": "Body",
            },
        )
        assert resp.status_code == 422

    async def test_create_feedback_message_too_long(self, client: AsyncClient):
        resp = await client.post(
            "/api/feedback",
            json={
                "email": "test@example.com",
                "theme": "Test",
                "message": "x" * 5001,
            },
        )
        assert resp.status_code == 422

    async def test_create_feedback_sanitizes_theme_and_message(
        self, client: AsyncClient, mock_notify: AsyncMock
    ):
        resp = await client.post(
            "/api/feedback",
            json={
                "email": "test@example.com",
                "theme": "  Hello\x00 world  ",
                "message": "  Great\x00 site!  ",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["theme"] == "Hello world"
        assert data["message"] == "Great site!"
        mock_notify.assert_called_once()


class TestListFeedback:
    async def test_list_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/feedback")
        assert resp.status_code == 401

    async def test_list_feedback(
        self, auth_client: AsyncClient, registry: DatabaseRegistry
    ):
        await create_feedback(registry, theme="First")
        await create_feedback(registry, theme="Second")
        resp = await auth_client.get("/api/feedback")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        themes = {item["theme"] for item in data["items"]}
        assert themes == {"First", "Second"}

    async def test_list_empty(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/feedback")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["per_page"] == 9

    async def test_list_pagination_and_status_filter(
        self, auth_client: AsyncClient, registry: DatabaseRegistry
    ):
        await create_feedback(registry, theme="Unread", status="unread")
        await create_feedback(registry, theme="Archived", status="archived")
        resp = await auth_client.get(
            "/api/feedback",
            params={"status": "unread", "page": 1, "per_page": 1},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["theme"] == "Unread"


class TestUpdateFeedbackStatus:
    async def test_update_status_requires_auth(self, client: AsyncClient):
        resp = await client.patch("/api/feedback/1/status", json={"status": "read"})
        assert resp.status_code == 401

    async def test_mark_as_read(
        self, auth_client: AsyncClient, registry: DatabaseRegistry
    ):
        fb = await create_feedback(registry)
        resp = await auth_client.patch(
            f"/api/feedback/{fb.id}/status", json={"status": "read"}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "read"

    async def test_mark_as_archived(
        self, auth_client: AsyncClient, registry: DatabaseRegistry
    ):
        fb = await create_feedback(registry)
        resp = await auth_client.patch(
            f"/api/feedback/{fb.id}/status", json={"status": "archived"}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "archived"

    async def test_invalid_status(
        self, auth_client: AsyncClient, registry: DatabaseRegistry
    ):
        fb = await create_feedback(registry)
        resp = await auth_client.patch(
            f"/api/feedback/{fb.id}/status", json={"status": "deleted"}
        )
        assert resp.status_code == 422
