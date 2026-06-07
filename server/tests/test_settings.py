import pytest

from app.settings import Settings, get_settings


def test_production_requires_telegram_allowlist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "production-jwt-key-with-32-characters-minimum")
    monkeypatch.setenv("RABBITMQ_PASSWORD", "production-rabbitmq-password-ok")
    monkeypatch.setenv("TELEGRAM_BOT_TO_DO_TOKEN", "123456:ABC")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_ID", "0")
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="TELEGRAM_ALLOWED_USER_ID"):
        Settings()

    get_settings.cache_clear()


def test_production_requires_strong_postgres_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "production-jwt-key-with-32-characters-minimum")
    monkeypatch.setenv("RABBITMQ_PASSWORD", "production-rabbitmq-password-ok")
    monkeypatch.setenv("POSTGRES_PASSWORD", "glorng")
    monkeypatch.setenv(
        "REDIS_URL",
        "redis://:production-redis-password-ok@redis:6379/0",
    )
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="POSTGRES_PASSWORD"):
        Settings()

    get_settings.cache_clear()


def test_production_requires_strong_redis_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "production-jwt-key-with-32-characters-minimum")
    monkeypatch.setenv("RABBITMQ_PASSWORD", "production-rabbitmq-password-ok")
    monkeypatch.setenv("POSTGRES_PASSWORD", "production-postgres-password-ok")
    monkeypatch.setenv("REDIS_URL", "redis://:replace-with-redis-password@redis:6379/0")
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="REDIS_PASSWORD"):
        Settings()

    get_settings.cache_clear()
