"""Dead-letter queue helpers for Celery task failures."""

from __future__ import annotations

import re
from typing import Any

from kombu import Exchange, Queue

from app.core.logging import logger

CELERY_QUEUE_NAME = "celery"
CELERY_DLQ_NAME = "celery.dlq"
CELERY_DLX_NAME = "celery.dlx"

celery_exchange = Exchange("celery", type="direct", durable=True)
celery_dlx = Exchange(CELERY_DLX_NAME, type="direct", durable=True)

celery_queue = Queue(
    CELERY_QUEUE_NAME,
    exchange=celery_exchange,
    routing_key=CELERY_QUEUE_NAME,
    durable=True,
    queue_arguments={
        "x-dead-letter-exchange": CELERY_DLX_NAME,
        "x-dead-letter-routing-key": CELERY_DLQ_NAME,
    },
)

celery_dlq = Queue(
    CELERY_DLQ_NAME,
    exchange=celery_dlx,
    routing_key=CELERY_DLQ_NAME,
    durable=True,
)

_SENSITIVE_KEYS = frozenset(
    {
        "token",
        "password",
        "secret",
        "access_token",
        "refresh_token",
        "authorization",
        "api_key",
        "apikey",
    }
)
_JWT_RE = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


def _redact_value(key: str | None, value: object) -> object:
    if key is not None and key.lower() in _SENSITIVE_KEYS:
        return "[redacted]"
    if isinstance(value, str) and _JWT_RE.match(value) and len(value) > 40:
        return "[redacted]"
    if isinstance(value, dict):
        return {str(k): _redact_value(str(k), v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_value(None, item) for item in value]
    if isinstance(value, tuple):
        return [_redact_value(None, item) for item in value]
    return value


def redact_task_payload(
    args: tuple[Any, ...] | list[Any] | None,
    kwargs: dict[str, Any] | None,
) -> tuple[list[object], dict[str, object]]:
    """Strip JWTs and known secret fields before DLQ / log persistence."""
    safe_args = [_redact_value(None, item) for item in (args or ())]
    safe_kwargs = {
        str(k): _redact_value(str(k), v) for k, v in dict(kwargs or {}).items()
    }
    return safe_args, safe_kwargs


def publish_dead_letter(
    *,
    task_name: str,
    task_id: str | None,
    args: tuple[Any, ...] | list[Any] | None,
    kwargs: dict[str, Any] | None,
    retries: int,
    exc: BaseException,
) -> None:
    """Persist a failed task payload on the DLQ (workers do not consume it)."""
    from app.workers.celery_app import celery_app

    safe_args, safe_kwargs = redact_task_payload(args, kwargs)
    payload = {
        "task": task_name,
        "id": task_id,
        "args": safe_args,
        "kwargs": safe_kwargs,
        "retries": retries,
        "exception": f"{type(exc).__name__}: {exc}",
    }
    if celery_app.conf.task_always_eager:
        logger.warning(
            "Dead-letter skipped in eager mode",
            context={
                "task_name": task_name,
                "task_id": task_id,
                "exception": payload["exception"],
            },
        )
        return
    try:
        with celery_app.producer_pool.acquire(block=True) as producer:
            producer.publish(
                payload,
                exchange=celery_dlx,
                routing_key=CELERY_DLQ_NAME,
                serializer="json",
                delivery_mode=2,
                declare=[celery_dlx, celery_dlq],
            )
        logger.warning(
            "Published task to dead-letter queue",
            context={
                "task_name": task_name,
                "task_id": task_id,
                "queue": CELERY_DLQ_NAME,
            },
        )
    except Exception as publish_exc:
        logger.error(
            "Failed to publish task to dead-letter queue",
            error=publish_exc,
            context={"task_name": task_name, "task_id": task_id},
        )
