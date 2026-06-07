"""Inbound webhook endpoints for external automation."""

from typing import Any

from fastapi import APIRouter, Depends, Request

from app.core.deps import AppSettings
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.rate_limit import RateLimiter
from app.db.deps import DbRegistry
from app.services.webhooks import (
    dispatch_webhook,
    parse_webhook_json,
    verify_webhook_signature,
    webhook_secret_for_slug,
)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

rate_limit_webhook = RateLimiter(requests=30, window=60)


@router.post(
    "/{slug}",
    summary="Inbound webhook",
    description=(
        "HMAC-signed webhook for external automation. "
        "Requires X-Glorng-Signature: sha256=<hex> and WEBHOOK_SECRETS config."
    ),
    dependencies=[Depends(rate_limit_webhook)],
)
async def receive_webhook(
    slug: str,
    request: Request,
    registry: DbRegistry,
    settings: AppSettings,
) -> dict[str, Any]:
    secret = webhook_secret_for_slug(settings, slug)
    if not secret:
        raise NotFoundError(f"Webhook slug not configured: {slug}")

    body = await request.body()
    signature = request.headers.get("x-glorng-signature")
    verify_webhook_signature(secret=secret, body=body, header=signature)

    if not body:
        raise ForbiddenError("Webhook body is required")

    payload = parse_webhook_json(body)
    return await dispatch_webhook(registry=registry, slug=slug, payload=payload)
