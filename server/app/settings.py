import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal
from urllib.parse import urlparse

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from sqlalchemy.engine import make_url

_WEAK_SECRET_MARKERS = ("do-not-use", "changeme", "replace-with", "secret")


def _validate_production_password(name: str, value: str, *, min_len: int) -> None:
    if len(value) < min_len or any(m in value.lower() for m in _WEAK_SECRET_MARKERS):
        msg = f"{name} is too weak for production; use {min_len}+ chars"
        raise ValueError(msg)


def _password_from_redis_url(url: str) -> str:
    return urlparse(url).password or ""


_COMPOSE_DB_HOST = "db"
_COMPOSE_DB_PORT = 5432
_HOST_DB_HOST = "127.0.0.1"
_HOST_DB_PORT = 5433
_COMPOSE_ES_HOST = "elasticsearch"
_COMPOSE_ES_PORT = 9200
_HOST_ES_HOST = "127.0.0.1"
_HOST_ES_PORT = 9200
_COMPOSE_MONGO_HOST = "mongodb"
_COMPOSE_MONGO_PORT = 27017
_HOST_MONGO_HOST = "127.0.0.1"
_HOST_MONGO_PORT = 27017


def _resolve_database_url(url: str) -> str:
    """Map Docker Compose DB host to localhost when running on the host."""
    if Path("/.dockerenv").exists():
        return url
    parsed = make_url(url)
    compose_port = parsed.port or _COMPOSE_DB_PORT
    if parsed.host == _COMPOSE_DB_HOST and compose_port == _COMPOSE_DB_PORT:
        parsed = parsed.set(host=_HOST_DB_HOST, port=_HOST_DB_PORT)
    return parsed.render_as_string(hide_password=False)


def _resolve_elasticsearch_url(url: str) -> str:
    """Map Docker Compose Elasticsearch host to localhost when running on the host."""
    if Path("/.dockerenv").exists():
        return url
    parsed = urlparse(url)
    port = parsed.port or _COMPOSE_ES_PORT
    if parsed.hostname == _COMPOSE_ES_HOST and port == _COMPOSE_ES_PORT:
        return parsed._replace(netloc=f"{_HOST_ES_HOST}:{_HOST_ES_PORT}").geturl()
    return url


def _resolve_mongodb_url(url: str) -> str:
    """Map Docker Compose MongoDB host to localhost when running on the host."""
    if Path("/.dockerenv").exists():
        return url
    parsed = urlparse(url)
    port = parsed.port or _COMPOSE_MONGO_PORT
    if parsed.hostname == _COMPOSE_MONGO_HOST and port == _COMPOSE_MONGO_PORT:
        auth = ""
        if parsed.username:
            auth = parsed.username
            if parsed.password is not None:
                auth = f"{auth}:{parsed.password}"
            auth = f"{auth}@"
        netloc = f"{auth}{_HOST_MONGO_HOST}:{_HOST_MONGO_PORT}"
        return parsed._replace(netloc=netloc).geturl()
    return url


def _parse_env_list(value: Any) -> list[str]:
    """Parse list settings from env: JSON array or comma-separated string."""
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        if stripped.startswith("["):
            parsed = json.loads(stripped)
            if not isinstance(parsed, list):
                msg = "Expected a JSON array"
                raise TypeError(msg)
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [part.strip() for part in stripped.split(",") if part.strip()]
    return [str(value).strip()]


def _parse_env_dict(value: Any) -> dict[str, str]:
    """Parse dict settings from env: JSON object only."""
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items()}
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return {}
        parsed = json.loads(stripped)
        if not isinstance(parsed, dict):
            msg = "Expected a JSON object"
            raise TypeError(msg)
        return {str(k): str(v) for k, v in parsed.items()}
    msg = "Expected a JSON object or dict"
    raise TypeError(msg)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    @field_validator("GITHUB_ALLOWED_USERS", "CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_list_fields(cls, value: Any) -> list[str]:
        return _parse_env_list(value)

    @field_validator("WEBHOOK_SECRETS", mode="before")
    @classmethod
    def _parse_webhook_secrets(cls, value: Any) -> dict[str, str]:
        return _parse_env_dict(value)

    @model_validator(mode="after")
    def _check_production_secrets(self) -> Settings:
        if self.APP_ENV == "production" and (
            len(self.JWT_SECRET) < 32
            or any(m in self.JWT_SECRET.lower() for m in _WEAK_SECRET_MARKERS)
        ):
            msg = "JWT_SECRET is too weak for production; use 32+ chars"
            raise ValueError(msg)
        if self.APP_ENV == "production" and any(
            origin.strip() == "*" for origin in self.CORS_ORIGINS
        ):
            msg = "CORS_ORIGINS cannot include '*' when allow_credentials is enabled"
            raise ValueError(msg)
        if self.APP_ENV == "production" and (
            len(self.RABBITMQ_PASSWORD) < 16
            or any(m in self.RABBITMQ_PASSWORD.lower() for m in _WEAK_SECRET_MARKERS)
        ):
            msg = "RABBITMQ_PASSWORD is too weak for production; use 16+ chars"
            raise ValueError(msg)
        if (
            self.APP_ENV == "production"
            and self.TELEGRAM_BOT_TO_DO_TOKEN
            and not self.TELEGRAM_ALLOWED_USER_ID
        ):
            msg = (
                "TELEGRAM_ALLOWED_USER_ID must be set when "
                "TELEGRAM_BOT_TO_DO_TOKEN is configured in production"
            )
            raise ValueError(msg)
        if self.APP_ENV == "production":
            _validate_production_password(
                "REDIS_PASSWORD",
                _password_from_redis_url(self.REDIS_URL),
                min_len=16,
            )
            if self.enable_postgres():
                _validate_production_password(
                    "POSTGRES_PASSWORD",
                    self.POSTGRES_PASSWORD,
                    min_len=16,
                )
            if self.enable_mongodb():
                _validate_production_password(
                    "MONGODB_PASSWORD",
                    self.MONGODB_PASSWORD,
                    min_len=16,
                )
        return self

    # Database backends
    ENABLE_MONGODB: bool = True
    ENABLE_POSTGRES: bool = False
    PRIMARY_DATABASE: Literal["mongodb"] = "mongodb"
    RUN_MIGRATIONS: bool = False

    # Postgres (optional secondary store)
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    # Database URL (required when ENABLE_POSTGRES; sqlite allowed only in dev/test)
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def _validate_database_backends(self) -> Settings:
        if self.enable_mongodb() and not self.MONGODB_URL.strip():
            msg = "MONGODB_URL is required when ENABLE_MONGODB is true"
            raise ValueError(msg)
        if self.enable_postgres():
            if not self.DATABASE_URL.strip():
                msg = "DATABASE_URL is required when ENABLE_POSTGRES is true"
                raise ValueError(msg)
            if not self.POSTGRES_USER or not self.POSTGRES_DB:
                msg = (
                    "POSTGRES_USER and POSTGRES_DB required "
                    "when ENABLE_POSTGRES is true"
                )
                raise ValueError(msg)
        if self.DATABASE_URL.startswith("sqlite") and self.APP_ENV not in {
            "development",
            "test",
        }:
            msg = "SQLite is only allowed when APP_ENV is development or test"
            raise ValueError(msg)
        if self.APP_ENV in {"production", "staging"} and not self.enable_mongodb():
            msg = "MongoDB must be enabled in production and staging"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _normalize_database_url(self) -> Settings:
        if not self.DATABASE_URL.strip():
            return self
        url = self.DATABASE_URL
        for token, value in {
            "${POSTGRES_USER}": self.POSTGRES_USER,
            "${POSTGRES_PASSWORD}": self.POSTGRES_PASSWORD,
            "${POSTGRES_DB}": self.POSTGRES_DB,
        }.items():
            url = url.replace(token, value)

        parsed = make_url(url)
        if parsed.host in {_COMPOSE_DB_HOST, _HOST_DB_HOST, "localhost"}:
            parsed = parsed.set(
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                database=self.POSTGRES_DB,
            )

        self.DATABASE_URL = _resolve_database_url(
            parsed.render_as_string(hide_password=False)
        )
        return self

    def enable_mongodb(self) -> bool:
        return self.ENABLE_MONGODB

    def enable_postgres(self) -> bool:
        return self.ENABLE_POSTGRES

    # Elasticsearch (optional; empty disables the external search backend)
    ELASTICSEARCH_URL: str = ""
    ELASTICSEARCH_INDEX: str = "search_documents"

    @model_validator(mode="after")
    def _normalize_elasticsearch_url(self) -> Settings:
        if self.ELASTICSEARCH_URL:
            self.ELASTICSEARCH_URL = _resolve_elasticsearch_url(self.ELASTICSEARCH_URL)
        return self

    def elasticsearch_enabled(self) -> bool:
        return bool(self.ELASTICSEARCH_URL.strip())

    # MongoDB (primary document store)
    MONGODB_USER: str = ""
    MONGODB_PASSWORD: str = ""
    MONGODB_DB: str = "glorng"
    MONGODB_URL: str = ""

    @model_validator(mode="after")
    def _normalize_mongodb_url(self) -> Settings:
        if not self.MONGODB_URL:
            return self

        url = self.MONGODB_URL
        for token, value in {
            "${MONGODB_USER}": self.MONGODB_USER,
            "${MONGODB_PASSWORD}": self.MONGODB_PASSWORD,
            "${MONGODB_DB}": self.MONGODB_DB,
        }.items():
            url = url.replace(token, value)

        self.MONGODB_URL = _resolve_mongodb_url(url)
        return self

    def mongodb_enabled(self) -> bool:
        """Whether a MongoDB URL is configured."""
        return bool(self.MONGODB_URL.strip())

    # Redis
    REDIS_URL: str

    # RabbitMQ / Celery
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    CELERY_BROKER_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # Auth
    ALLOWED_EMAIL: str = "admin@glorng.dev"

    # Email
    EMAIL_BACKEND: str = "console"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@glorng.dev"

    # Sentry (off in development unless SENTRY_ENABLED=true)
    SENTRY_ENABLED: bool = False
    SERVER_SENTRY_DSN: str = ""
    SERVER_SENTRY_RELEASE: str = ""

    def sentry_enabled(self) -> bool:
        """Whether server/worker Sentry should initialize."""
        if not self.SERVER_SENTRY_DSN:
            return False
        if self.SENTRY_ENABLED:
            return True
        return self.APP_ENV != "development"

    # Telegram Bot
    TELEGRAM_BOT_TO_DO_TOKEN: str = ""
    TELEGRAM_BOT_CHAT_TOKEN: str = ""
    TELEGRAM_ALLOWED_USER_ID: int = 0
    TIMEZONE: str = "Europe/Amsterdam"
    EXPENSE_DEFAULT_CURRENCY: str = "PLN"

    # Google Calendar
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = ""
    GITHUB_ALLOWED_USERS: Annotated[list[str], NoDecode] = []
    GITHUB_PUBLIC_USERNAME: str = ""

    # Donations
    STRIPE_LINK: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_DONATION_AMOUNT_CENTS: int = 500
    STRIPE_DONATION_CURRENCY: str = "usd"
    STRIPE_CHECKOUT_SUCCESS_URL: str = ""
    STRIPE_CHECKOUT_CANCEL_URL: str = ""
    TELEGRAM_LINK: str = ""
    CRYPTO_BTC_ADDRESS: str = ""
    CRYPTO_ETH_ADDRESS: str = ""

    # Inbound webhooks (slug → HMAC secret)
    WEBHOOK_SECRETS: Annotated[dict[str, str], NoDecode] = {}

    # Spotify
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    SPOTIFY_REFRESH_TOKEN: str = ""

    # AI provider API keys (OpenAI-compatible APIs via LLM_BASE_URL)
    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4.1"
    LLM_BASE_URL: str = ""
    AI_CHAT_ENABLED: bool = True
    AI_SEARCH_ENABLED: bool = True

    # Task intake (Telegram AI)
    TASK_INTAKE_AI_ENABLED: bool = True
    TASK_INTAKE_CONFIDENCE_THRESHOLD: float = 0.7

    # CORS
    CORS_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost",
        "http://localhost:80",
    ]

    # Seed
    SEED_PASSWORD: str = ""

    # App
    APP_ENV: str = "development"
    LOG_REQUESTS: bool = True
    LOG_REQUEST_BODIES: bool = False
    CELERY_TASK_ALWAYS_EAGER: bool = False
    APP_LOG_PERSIST_ENABLED: bool = True
    APP_LOG_PERSIST_MIN_LEVEL: str = "INFO"
    APP_LOG_RETENTION_DAYS: int = 30
    APP_NAME: str = "Gleb.Y"
    BASE_URL: str = "http://localhost"
    MEDIA_DIR: str = "/app/media"

    # Weather
    WEATHER_DEFAULT_LABEL: str = "Wrocław"
    WEATHER_DEFAULT_QUERY: str = "Wroclaw"
    WORLD_TIME_API_BASE: str = "https://timeapi.world/api"

    def stripe_checkout_enabled(self) -> bool:
        """Whether Stripe Checkout sessions can be created."""
        return bool(self.STRIPE_SECRET_KEY)

    def stripe_webhook_enabled(self) -> bool:
        """Whether Stripe webhook signature verification is configured."""
        return bool(self.STRIPE_WEBHOOK_SECRET)

    def github_public_username(self) -> str | None:
        """Public GitHub username for portfolio repo listing."""
        if self.GITHUB_PUBLIC_USERNAME.strip():
            return self.GITHUB_PUBLIC_USERNAME.strip()
        if self.GITHUB_ALLOWED_USERS:
            return self.GITHUB_ALLOWED_USERS[0]
        return None


@lru_cache
def get_settings() -> Settings:
    return Settings()
