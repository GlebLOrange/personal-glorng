"""Non-blocking persistence of structured logs to MongoDB."""

from __future__ import annotations

import asyncio
import json
import queue
import sys
import traceback
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.db.documents.app_log import AppLog

LOG_QUEUE_MAX = 10_000
BATCH_SIZE = 50
FLUSH_INTERVAL_SEC = 1.0
_MAX_BSON_BYTES = 15 * 1024 * 1024

_LEVEL_ORDER = {"debug": 10, "info": 20, "warning": 30, "error": 40}

_SECRET_KEYS = frozenset(
    {
        "password",
        "token",
        "authorization",
        "cookie",
        "secret",
        "api_key",
        "access_token",
        "refresh_token",
    },
)

_log_queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=LOG_QUEUE_MAX)
_worker_task: asyncio.Task[None] | None = None
_running = False


def _level_value(level: str) -> int:
    return _LEVEL_ORDER.get(level.lower(), 0)


def _should_persist(entry: dict[str, Any]) -> bool:
    from app.settings import get_settings

    settings = get_settings()
    if not settings.APP_LOG_PERSIST_ENABLED:
        return False
    min_level = _level_value(settings.APP_LOG_PERSIST_MIN_LEVEL)
    if _level_value(str(entry.get("level", "info"))) < min_level:
        return False
    return entry.get("path") != "/api/health"


def enqueue_log_entry(entry: dict[str, Any]) -> None:
    """Enqueue one log entry; drop oldest when the buffer is full."""
    if not _should_persist(entry):
        return
    try:
        _log_queue.put_nowait(entry)
    except queue.Full:
        try:
            _log_queue.get_nowait()
            _log_queue.put_nowait(entry)
        except queue.Empty:
            pass


def _drain_queue(*, max_items: int | None = None) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    while max_items is None or len(entries) < max_items:
        try:
            entries.append(_log_queue.get_nowait())
        except queue.Empty:
            break
    return entries


def _truncate_str(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3] + "..."


def _is_secret_key(key: str) -> bool:
    lowered = key.lower()
    return lowered in _SECRET_KEYS or any(
        marker in lowered for marker in ("password", "token", "secret", "authorization")
    )


def _sanitize_value(value: object) -> object:
    if isinstance(value, dict):
        return _sanitize_context(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value[:50]]
    if isinstance(value, str):
        return _truncate_str(value, 512)
    return value


def _sanitize_context(context: dict[str, Any] | None) -> dict[str, Any] | None:
    if not context:
        return None
    sanitized: dict[str, Any] = {}
    for key, value in context.items():
        if _is_secret_key(key):
            sanitized[key] = "[REDACTED]"
        else:
            sanitized[key] = _sanitize_value(value)
    encoded = json.dumps(sanitized, default=str)
    if len(encoded) <= _context_limit():
        return sanitized
    return {"_truncated": True, "preview": encoded[: _context_limit()]}


def _context_limit() -> int:
    from app.settings import get_settings

    return get_settings().APP_LOG_MAX_CONTEXT_CHARS


def _sanitize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    from app.settings import get_settings

    settings = get_settings()
    sanitized = dict(entry)
    sanitized["message"] = _truncate_str(
        str(sanitized.get("message", "")),
        settings.APP_LOG_MAX_MESSAGE_CHARS,
    )
    if sanitized.get("traceback") is not None:
        sanitized["traceback"] = _truncate_str(
            str(sanitized["traceback"]),
            settings.APP_LOG_MAX_TRACEBACK_CHARS,
        )
    if sanitized.get("error") is not None:
        sanitized["error"] = _truncate_str(str(sanitized["error"]), 2048)
    return sanitized


_KNOWN_ENTRY_KEYS = frozenset(
    {
        "timestamp",
        "level",
        "message",
        "logger",
        "service",
        "error",
        "error_type",
        "traceback",
    },
)


def _extract_context(entry: dict[str, Any]) -> dict[str, Any] | None:
    context = {
        key: value
        for key, value in entry.items()
        if key not in _KNOWN_ENTRY_KEYS and value is not None
    }
    return context or None


def _entry_to_app_log(entry: dict[str, Any]) -> AppLog:
    from app.db.documents.app_log import AppLog
    from app.settings import get_settings

    settings = get_settings()
    sanitized = _sanitize_entry(entry)
    raw_context = _extract_context(sanitized)
    context = _sanitize_context(raw_context) if raw_context else None
    request_id = None
    if sanitized.get("request_id") is not None:
        request_id = str(sanitized["request_id"])
    elif context and context.get("request_id") is not None:
        request_id = str(context["request_id"])

    occurred_raw = sanitized.get("timestamp")
    occurred_at = (
        datetime.fromisoformat(occurred_raw)
        if isinstance(occurred_raw, str)
        else None
    )

    return AppLog(
        id=0,
        occurred_at=occurred_at,
        level=str(sanitized.get("level", "info")).lower(),
        message=str(sanitized.get("message", "")),
        logger=str(sanitized.get("logger", "glorng")),
        service=str(sanitized.get("service", settings.APP_SERVICE_NAME)),
        context=context,
        error=sanitized.get("error"),
        error_type=sanitized.get("error_type"),
        traceback=sanitized.get("traceback"),
        request_id=request_id,
    )


def _estimate_doc_bytes(log: AppLog) -> int:
    payload = {
        "id": log.id,
        "occurred_at": log.occurred_at.isoformat() if log.occurred_at else None,
        "level": log.level,
        "message": log.message,
        "logger": log.logger,
        "service": log.service,
        "context": log.context,
        "error": log.error,
        "error_type": log.error_type,
        "traceback": log.traceback,
        "request_id": log.request_id,
    }
    return len(json.dumps(payload, default=str).encode())


def _write_persist_error(message: str, error: Exception) -> None:
    sys.stderr.write(
        json.dumps(
            {
                "level": "error",
                "message": message,
                "error": str(error),
                "error_type": type(error).__name__,
                "traceback": traceback.format_exc(),
            },
            default=str,
        )
        + "\n",
    )


async def _flush_batch(entries: list[dict[str, Any]]) -> None:
    if not entries:
        return
    try:
        from app.core.mongodb import get_mongodb_database
        from app.db.repositories.app_log import AppLogRepository

        repo = AppLogRepository(get_mongodb_database())
        logs = [_entry_to_app_log(entry) for entry in entries]
        logs = [log for log in logs if _estimate_doc_bytes(log) <= _MAX_BSON_BYTES]
        if logs:
            await repo.insert_many(logs)
    except Exception as exc:
        _write_persist_error("App log persist failed", exc)


async def _worker_loop() -> None:
    while _running:
        batch = _drain_queue(max_items=BATCH_SIZE)
        if batch:
            await _flush_batch(batch)
        if not _running:
            break
        await asyncio.sleep(FLUSH_INTERVAL_SEC)

    final_batch = _drain_queue()
    if final_batch:
        await _flush_batch(final_batch)


async def start_app_log_worker() -> None:
    """Start the background MongoDB log drain task."""
    global _worker_task, _running
    if _worker_task is not None:
        return
    _running = True
    _worker_task = asyncio.create_task(_worker_loop())


async def stop_app_log_worker() -> None:
    """Stop the worker and flush any queued entries."""
    global _worker_task, _running
    _running = False
    if _worker_task is None:
        return
    await _worker_task
    _worker_task = None
