"""Tests for Stripe donation checkout and webhooks."""

import hashlib
import hmac
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.routers.donations import STRIPE_WEBHOOK_MAX_BODY_BYTES
from app.services.stripe_donations import create_checkout_session
from app.settings import get_settings
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
async def test_create_checkout_session_sends_donate_metadata() -> None:
    """Checkout Session form body includes donate CTA and donation metadata."""
    get_settings.cache_clear()
    settings = get_settings()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "cs_test_meta",
        "url": "https://checkout.stripe.com/c/pay/cs_test_meta",
    }
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch(
        "app.services.stripe_donations.httpx.AsyncClient",
        return_value=mock_client,
    ):
        result = await create_checkout_session(settings)

    assert result["session_id"] == "cs_test_meta"
    posted = mock_client.post.call_args.kwargs["data"]
    assert posted["submit_type"] == "donate"
    assert posted["metadata[purpose]"] == "donation"
    assert posted["metadata[source]"] == "portfolio"


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
        "id": "evt_test_checkout_1",
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
async def test_stripe_webhook_deduplicates_replay(
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
        "id": "evt_test_dup_1",
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
    headers = {"Stripe-Signature": _stripe_signature(body, "whsec_test")}

    first = await client.post("/api/donations/webhook", content=body, headers=headers)
    second = await client.post("/api/donations/webhook", content=body, headers=headers)

    assert first.status_code == 200
    assert first.json()["status"] == "processed"
    assert second.status_code == 200
    assert second.json()["status"] == "duplicate"
    assert len(notified) == 1


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
