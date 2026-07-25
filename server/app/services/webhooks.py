"""Inbound webhook signature verification and dispatch."""

import hashlib
import hmac
import json
from typing import Any

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.logging import logger
from app.db.documents.audit import AuditActorType, AuditCategory, AuditSource
from app.db.registry import DatabaseRegistry
from app.services.audit import AuditRecord, AuditService
from app.settings import Settings

_SIGNATURE_PREFIX = "sha256="


def parse_webhook_secrets(raw: dict[str, str]) -> dict[str, str]:
    """Return slug → secret mapping with non-empty values only."""
    return {
        slug.strip(): secret for slug, secret in raw.items() if slug.strip() and secret
    }


def verify_webhook_signature(*, secret: str, body: bytes, header: str | None) -> None:
    """Validate HMAC-SHA256 signature from X-Glorng-Signature header."""
    if not header or not header.startswith(_SIGNATURE_PREFIX):
        raise ForbiddenError("Missing or invalid webhook signature")

    provided = header.removeprefix(_SIGNATURE_PREFIX).strip().lower()
    expected = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(provided, expected):
        logger.warning("Webhook signature mismatch")
        raise ForbiddenError("Invalid webhook signature")


def webhook_secret_for_slug(settings: Settings, slug: str) -> str | None:
    """Return configured secret for slug, or None if webhooks are disabled."""
    secrets = parse_webhook_secrets(settings.WEBHOOK_SECRETS)
    return secrets.get(slug)


async def dispatch_webhook(
    *,
    registry: DatabaseRegistry,
    slug: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Route a verified webhook payload to the appropriate service."""
    # ponytail: ping ignores body fields; payload kept so the router always parses JSON
    _ = payload

    if slug == "ping":
        await AuditService(registry).record(
            AuditRecord(
                category=AuditCategory.SYSTEM,
                action="webhook.ping",
                actor_type=AuditActorType.ANONYMOUS,
                source=AuditSource.API,
                metadata={"slug": slug},
            ),
        )
        return {"ok": True}

    msg = f"Unknown webhook slug: {slug}"
    raise NotFoundError(msg)


def parse_webhook_json(body: bytes) -> dict[str, Any]:
    """Parse webhook JSON body; raise ValidationError on invalid input."""
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValidationError("Webhook body must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValidationError("Webhook JSON root must be an object")
    return parsed
