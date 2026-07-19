"""Stripe Checkout and webhook handling for donations."""

import hashlib
import hmac
import json
import time
from typing import Any

import httpx

from app.core.exceptions import ApiError, ForbiddenError
from app.core.logging import logger
from app.core.redis import cache_set_nx
from app.core.redis_keys import STRIPE_EVENT_PREFIX
from app.core.telegram import notify_admin
from app.settings import Settings, get_settings

_STRIPE_API_BASE = "https://api.stripe.com/v1"
_SIGNATURE_TOLERANCE_SECONDS = 300
# Stripe retries webhooks for up to ~3 days; keep a buffer for late deliveries.
_STRIPE_EVENT_DEDUP_TTL_SECONDS = 60 * 60 * 24 * 7


async def create_checkout_session(settings: Settings | None = None) -> dict[str, str]:
    """Create a Stripe Checkout Session and return its URL."""
    active = settings or get_settings()
    if not active.stripe_checkout_enabled():
        raise ApiError(503, "Stripe Checkout is not configured")

    success_url = (
        active.STRIPE_CHECKOUT_SUCCESS_URL
        or f"{active.BASE_URL.rstrip('/')}/?donated=1"
    )
    cancel_url = active.STRIPE_CHECKOUT_CANCEL_URL or active.BASE_URL.rstrip("/")

    data = {
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "line_items[0][price_data][currency]": active.STRIPE_DONATION_CURRENCY.lower(),
        "line_items[0][price_data][unit_amount]": str(
            active.STRIPE_DONATION_AMOUNT_CENTS
        ),
        "line_items[0][price_data][product_data][name]": "Support gLOrng",
        "line_items[0][quantity]": "1",
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            f"{_STRIPE_API_BASE}/checkout/sessions",
            data=data,
            auth=(active.STRIPE_SECRET_KEY, ""),
        )

    if resp.status_code != 200:
        logger.error(
            "Stripe Checkout session creation failed",
            context={"status": resp.status_code, "body": resp.text[:500]},
        )
        raise ApiError(502, "Failed to create Stripe Checkout session")

    payload = resp.json()
    url = payload.get("url")
    session_id = payload.get("id")
    if not url or not session_id:
        raise ApiError(502, "Stripe returned an incomplete Checkout session")

    return {"url": url, "session_id": session_id}


def verify_stripe_signature(
    *,
    payload: bytes,
    signature_header: str | None,
    secret: str,
) -> None:
    """Verify Stripe-Signature header (t=timestamp,v1=signature)."""
    if not signature_header:
        raise ForbiddenError("Missing Stripe-Signature header")

    parts: dict[str, str] = {}
    for item in signature_header.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        parts[key.strip()] = value.strip()

    timestamp = parts.get("t")
    signature = parts.get("v1")
    if not timestamp or not signature:
        raise ForbiddenError("Invalid Stripe-Signature header")

    try:
        ts = int(timestamp)
    except ValueError as exc:
        raise ForbiddenError("Invalid Stripe-Signature timestamp") from exc

    if abs(time.time() - ts) > _SIGNATURE_TOLERANCE_SECONDS:
        raise ForbiddenError("Stripe webhook timestamp outside tolerance")

    signed_payload = f"{timestamp}.{payload.decode()}"
    expected = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        logger.warning("Stripe webhook signature mismatch")
        raise ForbiddenError("Invalid Stripe webhook signature")


async def handle_stripe_event(event: dict[str, Any]) -> dict[str, str]:
    """Dispatch a verified Stripe webhook event."""
    event_type = event.get("type", "")
    if event_type != "checkout.session.completed":
        return {"status": "ignored", "type": event_type}

    event_id = event.get("id")
    if isinstance(event_id, str) and event_id:
        claimed = await cache_set_nx(
            f"{STRIPE_EVENT_PREFIX}{event_id}",
            "1",
            _STRIPE_EVENT_DEDUP_TTL_SECONDS,
        )
        if claimed is False:
            logger.info(
                "Stripe webhook duplicate ignored",
                context={"event_id": event_id, "type": event_type},
            )
            return {"status": "duplicate", "type": event_type}

    session = event.get("data", {}).get("object", {})
    amount = session.get("amount_total")
    currency = session.get("currency", "")
    customer_email = session.get("customer_details", {}).get("email", "anonymous")

    text = (
        "<b>Donation received</b>\n"
        f"Amount: {amount} {str(currency).upper()}\n"
        f"Email: {customer_email}"
    )
    await notify_admin(text)
    logger.info(
        "Stripe donation completed",
        context={"amount": amount, "currency": currency, "event_id": event_id},
    )
    return {"status": "processed", "type": event_type}


def parse_stripe_event(payload: bytes) -> dict[str, Any]:
    """Parse Stripe webhook JSON payload."""
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        msg = "Stripe event must be a JSON object"
        raise TypeError(msg)
    return parsed
