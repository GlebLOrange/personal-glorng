"""Sentry initialization guards and error capture behavior."""

from unittest.mock import patch

import pytest

from app.core.logging import logger
from app.settings import get_settings


def test_sentry_disabled_without_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SERVER_SENTRY_DSN", "")
    monkeypatch.setenv("SENTRY_ENABLED", "false")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.sentry_enabled() is False
    get_settings.cache_clear()


def test_logger_capture_exception_on_error() -> None:
    error = ValueError("boom")
    with patch("sentry_sdk.capture_exception") as capture:
        logger.error("Task failed", error=error)
    capture.assert_called_once_with(error)
