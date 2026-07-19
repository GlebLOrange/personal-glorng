from pathlib import Path

import pytest

from app.settings import Settings, get_settings
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file, scenario_env


def test_settings_loads_when_groq_api_key_absent(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """GROQ_API_KEY is optional at startup; empty means AI features stay off."""
    env_file = scenario_env(tmp_path)
    lines = [
        line
        for line in env_file.read_text(encoding="utf-8").splitlines()
        if not line.startswith("GROQ_API_KEY=")
    ]
    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    activate_env_file(monkeypatch, env_file)

    settings = Settings()

    assert settings.GROQ_API_KEY == ""
    get_settings.cache_clear()


def test_production_requires_telegram_allowlist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "production-telegram.env")

    with pytest.raises(ValueError, match="TELEGRAM_ALLOWED_USER_ID"):
        Settings()

    get_settings.cache_clear()


def test_production_requires_strong_postgres_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "production-weak-postgres.env")

    with pytest.raises(ValueError, match="POSTGRES_PASSWORD"):
        Settings()

    get_settings.cache_clear()


def test_production_requires_strong_redis_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "production-weak-redis.env")

    with pytest.raises(ValueError, match="REDIS_PASSWORD"):
        Settings()

    get_settings.cache_clear()


def test_production_forbids_request_body_logging(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_file = scenario_env(
        tmp_path,
        base=ENV_SCENARIOS_DIR / "production-csrf.env",
        LOG_REQUEST_BODIES="true",
    )
    activate_env_file(monkeypatch, env_file)

    with pytest.raises(ValueError, match="LOG_REQUEST_BODIES"):
        Settings()

    get_settings.cache_clear()
