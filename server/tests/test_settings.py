import pytest

from app.settings import Settings, get_settings
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file


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
