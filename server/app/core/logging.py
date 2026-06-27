"""Structured JSON logger backed by Loguru."""

import json
import logging
import sys
import traceback
from typing import Any

import sentry_sdk
from loguru import logger as _loguru


def _build_log_entry(record: dict[str, Any]) -> dict[str, Any]:
    """Build a structured log dict from a Loguru record."""
    entry: dict[str, Any] = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name.lower(),
        "message": record["message"],
        "logger": record["name"] or "glorng",
    }
    extra = record.get("extra", {})
    if ctx := extra.get("context"):
        entry.update(ctx)
    if record["exception"]:
        entry["error"] = str(record["exception"].value)
        entry["error_type"] = type(record["exception"].value).__name__
        entry["traceback"] = "".join(
            traceback.format_exception(
                type(record["exception"].value),
                record["exception"].value,
                record["exception"].traceback,
            ),
        )
    return entry


def _json_sink(message: Any) -> None:  # noqa: ANN401
    """Serialize each log record as a single JSON line."""
    entry = _build_log_entry(message.record)
    sys.stderr.write(json.dumps(entry, default=str) + "\n")


def _persist_sink(message: Any) -> None:  # noqa: ANN401
    """Enqueue log records for MongoDB persistence."""
    from app.core.app_log_persist import enqueue_log_entry

    enqueue_log_entry(_build_log_entry(message.record))


_loguru.remove()
_loguru.add(_json_sink, level="DEBUG", serialize=False)
_loguru.add(_persist_sink, level="DEBUG", serialize=False)


class _InterceptHandler(logging.Handler):
    """Route stdlib logging into Loguru for third-party libs."""

    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = _loguru.level(record.levelname).name
        except ValueError:
            level = record.levelno
        _loguru.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[_InterceptHandler()], level=logging.INFO, force=True)


class StructuredLogger:
    """Thin wrapper preserving the project-wide logger interface."""

    def info(self, message: str, context: dict[str, Any] | None = None) -> None:
        _loguru.bind(context=context or {}).info(message)

    def warning(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        error: Exception | None = None,
    ) -> None:
        ctx = {**(context or {})}
        if error:
            ctx["error"] = str(error)
            ctx["error_type"] = type(error).__name__
        _loguru.opt(exception=error).bind(context=ctx).warning(message)

    def error(
        self,
        message: str,
        error: Exception | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        ctx = {**(context or {})}
        if error:
            ctx["error"] = str(error)
            ctx["error_type"] = type(error).__name__
            ctx["traceback"] = traceback.format_exc()
            sentry_sdk.capture_exception(error)
        _loguru.opt(exception=error).bind(context=ctx).error(message)

    def debug(self, message: str, context: dict[str, Any] | None = None) -> None:
        _loguru.bind(context=context or {}).debug(message)

    def exception(self, message: str, context: dict[str, Any] | None = None) -> None:
        _loguru.bind(context=context or {}).exception(message)


logger = StructuredLogger()
