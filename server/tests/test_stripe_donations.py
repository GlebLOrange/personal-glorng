"""Tests for Stripe donation checkout and webhooks."""

import hashlib
import hmac
import json
import time

import pytest
from httpx import AsyncClient

from app.routers.donations import STRIPE_WEBHOOK_MAX_BODY_BYTES
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file


def _stripe_signature(payload: bytes, secret: str) -> str:
    timestamp = str(int(time.time()))
    signed = f"{timestamp}.{payload.decode()}"
    digest = hmac.new(secret.encode(), signed.encode(), hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


@pytest.fixture(autouse=True)
def stripe_env(monkeypatch: pytest.MonkeyPatch) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "stripe.env")


@pytest.mark.asyncio
async def test_donations_config_includes_checkout_flag(client: AsyncClient) -> None:
    resp = await client.get("/api/donations/config")
    assert resp.status_code == 200
    stripe = resp.json()["stripe"]
    assert stripe["checkout_enabled"] is True


@pytest.mark.asyncio
async def test_create_checkout_session(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_create_checkout_session(settings=None) -> dict[str, str]:
        return {
            "url": "https://checkout.stripe.com/test",
            "session_id": "cs_test_123",
        }

    monkeypatch.setattr(
        "app.routers.donations.create_checkout_session",
        fake_create_checkout_session,
    )

    resp = await client.post("/api/donations/checkout")
    assert resp.status_code == 200
    assert resp.json()["url"].startswith("https://checkout.stripe.com/")


@pytest.mark.asyncio
async def test_stripe_webhook_checkout_completed(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    notified: list[str] = []

    async def fake_notify(text: str) -> None:
        notified.append(text)

    monkeypatch.setattr(
        "app.services.stripe_donations.notify_admin",
        fake_notify,
    )

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "amount_total": 500,
                "currency": "usd",
                "customer_details": {"email": "donor@example.com"},
            },
        },
    }
    body = json.dumps(event).encode()
    resp = await client.post(
        "/api/donations/webhook",
        content=body,
        headers={"Stripe-Signature": _stripe_signature(body, "whsec_test")},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "processed"
    assert notified


@pytest.mark.asyncio
async def test_stripe_webhook_rejects_invalid_signature(client: AsyncClient) -> None:
    body = b'{"type":"checkout.session.completed"}'
    resp = await client.post(
        "/api/donations/webhook",
        content=body,
        headers={"Stripe-Signature": "t=1,v1=bad"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_stripe_webhook_rejects_oversized_body(client: AsyncClient) -> None:
    body = b"x" * (STRIPE_WEBHOOK_MAX_BODY_BYTES + 1)
    resp = await client.post(
        "/api/donations/webhook",
        content=body,
        headers={"Stripe-Signature": _stripe_signature(body, "whsec_test")},
    )
    assert resp.status_code == 413
