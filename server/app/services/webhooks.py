"""Inbound webhook signature verification and dispatch."""

import hashlib
import hmac
import json
from datetime import UTC
from typing import Any

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.logging import logger
from app.db.documents.audit import AuditActorType, AuditCategory, AuditSource
from app.db.documents.feedback import Feedback
from app.db.registry import DatabaseRegistry
from app.schemas.feedback import FeedbackCreate
from app.schemas.task import TaskCreate
from app.services.audit import AuditRecord, AuditService
from app.services.search_indexers.feedback import index_feedback
from app.services.task import TaskService
from app.settings import Settings, get_settings

_SIGNATURE_PREFIX = "sha256="


def parse_webhook_secrets(raw: dict[str, str]) -> dict[str, str]:
    """Return slug → secret mapping with non-empty values only."""
    return {slug.strip(): secret for slug, secret in raw.items() if slug.strip() and secret}


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
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Route a verified webhook payload to the appropriate service."""
    active_settings = settings or get_settings()

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

    if slug == "task-create":
        return await _handle_task_create(registry, payload, active_settings)

    if slug == "feedback":
        return await _handle_feedback(registry, payload)

    msg = f"Unknown webhook slug: {slug}"
    raise NotFoundError(msg)


async def _handle_task_create(
    registry: DatabaseRegistry,
    payload: dict[str, Any],
    settings: Settings,
) -> dict[str, Any]:
    try:
        data = TaskCreate.model_validate(payload)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc

    telegram_user_id = data.telegram_user_id or settings.TELEGRAM_ALLOWED_USER_ID
    if not telegram_user_id:
        raise ValidationError(
            "telegram_user_id is required (set TELEGRAM_ALLOWED_USER_ID)",
        )

    scheduled_at = data.scheduled_at
    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=UTC)

    svc = TaskService(registry)
    task = await svc.create_with_sync(
        telegram_user_id=telegram_user_id,
        title=data.title,
        scheduled_at=scheduled_at,
        description=data.description,
        location=data.location,
        reminder_minutes=data.reminder_minutes,
        source=AuditSource.API,
        actor_type=AuditActorType.ANONYMOUS,
        actor_id=None,
    )
    return {"task_id": task.id, "title": task.title}


async def _handle_feedback(
    registry: DatabaseRegistry,
    payload: dict[str, Any],
) -> dict[str, Any]:
    if registry.feedback is None:
        msg = "Feedback repository is not initialized"
        raise RuntimeError(msg)

    try:
        data = FeedbackCreate.model_validate(payload)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc

    entry = Feedback(email=data.email, theme=data.theme, message=data.message)
    entry = await registry.feedback.insert(entry)
    await index_feedback(registry, entry)
    logger.info(
        "Feedback created via webhook",
        context={"id": entry.id, "email": data.email},
    )
    return {"feedback_id": entry.id}


def parse_webhook_json(body: bytes) -> dict[str, Any]:
    """Parse webhook JSON body; raise ValidationError on invalid input."""
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValidationError("Webhook body must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValidationError("Webhook JSON root must be an object")
    return parsed
