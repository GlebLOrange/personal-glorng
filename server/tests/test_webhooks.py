"""Tests for inbound webhooks."""

import hashlib
import hmac
import json

import pytest
from httpx import AsyncClient

from app.settings import get_settings


def _sign(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


@pytest.fixture(autouse=True)
def webhook_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "WEBHOOK_SECRETS",
        json.dumps(
            {
                "task-create": "task-secret",
                "feedback": "feedback-secret",
                "ping": "ping-secret",
            },
        ),
    )
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_ID", "123456789")
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_webhook_ping(client: AsyncClient) -> None:
    body = b"{}"
    resp = await client.post(
        "/api/webhooks/ping",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Glorng-Signature": _sign("ping-secret", body),
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


@pytest.mark.asyncio
async def test_webhook_rejects_bad_signature(client: AsyncClient) -> None:
    body = b"{}"
    resp = await client.post(
        "/api/webhooks/ping",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Glorng-Signature": "sha256=deadbeef",
        },
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_webhook_task_create(client: AsyncClient) -> None:
    payload = {
        "title": "Webhook task",
        "scheduled_at": "2026-06-08T10:00:00Z",
    }
    body = json.dumps(payload).encode()
    resp = await client.post(
        "/api/webhooks/task-create",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Glorng-Signature": _sign("task-secret", body),
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["task_id"] > 0
    assert data["title"] == "Webhook task"


@pytest.mark.asyncio
async def test_webhook_feedback(client: AsyncClient) -> None:
    payload = {
        "email": "visitor@example.com",
        "theme": "Hello",
        "message": "From webhook",
    }
    body = json.dumps(payload).encode()
    resp = await client.post(
        "/api/webhooks/feedback",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Glorng-Signature": _sign("feedback-secret", body),
        },
    )
    assert resp.status_code == 200
    assert resp.json()["feedback_id"] > 0


@pytest.mark.asyncio
async def test_webhook_unknown_slug(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/webhooks/unknown",
        content=b"{}",
        headers={"X-Glorng-Signature": "sha256=abc"},
    )
    assert resp.status_code == 404
