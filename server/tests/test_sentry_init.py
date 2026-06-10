"""Sentry initialization guards and error capture behavior."""

from unittest.mock import patch

from app.core.logging import logger
from app.settings import get_settings


def test_sentry_disabled_without_dsn() -> None:
    settings = get_settings()
    assert settings.sentry_enabled() is False


def test_logger_capture_exception_on_error() -> None:
    error = ValueError("boom")
    with patch("sentry_sdk.capture_exception") as capture:
        logger.error("Task failed", error=error)
    capture.assert_called_once_with(error)
