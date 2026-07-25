"""Tests for inbound webhooks."""

import hashlib
import hmac

import pytest
from httpx import AsyncClient

from app.routers.webhooks import WEBHOOK_MAX_BODY_BYTES
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file


def _sign(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


@pytest.fixture(autouse=True)
def webhook_env(monkeypatch: pytest.MonkeyPatch) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "webhooks.env")


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
async def test_webhook_rejects_oversized_body(client: AsyncClient) -> None:
    body = b"x" * (WEBHOOK_MAX_BODY_BYTES + 1)
    resp = await client.post(
        "/api/webhooks/ping",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Glorng-Signature": _sign("ping-secret", body),
        },
    )
    assert resp.status_code == 413


@pytest.mark.asyncio
async def test_webhook_unknown_slug(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/webhooks/unknown",
        content=b"{}",
        headers={"X-Glorng-Signature": "sha256=abc"},
    )
    assert resp.status_code == 404
