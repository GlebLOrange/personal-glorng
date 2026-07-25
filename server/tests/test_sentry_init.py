"""Sentry initialization guards and error capture behavior."""

from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.monkeypatch import MonkeyPatch

from app.core.logging import logger
from app.settings import get_settings
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file, scenario_env

_DSN = "https://examplePublicKey@o0.ingest.sentry.io/0"


def test_sentry_disabled_without_dsn() -> None:
    """Empty DSN keeps Sentry off regardless of other flags."""
    settings = get_settings()
    assert settings.sentry_enabled() is False


@pytest.mark.parametrize(
    ("app_env", "sentry_enabled_flag", "expected", "base_name"),
    [
        ("development", "false", False, None),
        ("development", "true", True, None),
        ("test", "false", False, None),
        ("test", "true", True, None),
        ("production", "false", True, "production-csrf.env"),
        ("staging", "false", True, None),
    ],
)
def test_sentry_enabled_matrix(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
    app_env: str,
    sentry_enabled_flag: str,
    expected: bool,
    base_name: str | None,
) -> None:
    """Local/test are opt-in; staging/production turn on when a DSN is set."""
    overrides: dict[str, str] = {
        "APP_ENV": app_env,
        "SERVER_SENTRY_DSN": _DSN,
        "SENTRY_ENABLED": sentry_enabled_flag,
    }
    base = ENV_SCENARIOS_DIR / base_name if base_name else None
    env_kwargs = {"base": base, **overrides} if base is not None else overrides
    activate_env_file(monkeypatch, scenario_env(tmp_path, **env_kwargs))
    try:
        assert get_settings().sentry_enabled() is expected
    finally:
        get_settings.cache_clear()


def test_logger_capture_exception_on_error() -> None:
    """Logger.error with an exception forwards to Sentry capture."""
    error = ValueError("boom")
    with patch("sentry_sdk.capture_exception") as capture:
        logger.error("Task failed", error=error)
    capture.assert_called_once_with(error)
