import json
from functools import lru_cache
from typing import Annotated, Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_WEAK_SECRET_MARKERS = ("do-not-use", "changeme", "replace-with", "secret")


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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    @field_validator("GITHUB_ALLOWED_USERS", "CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_list_fields(cls, value: Any) -> list[str]:
        return _parse_env_list(value)

    @model_validator(mode="after")
    def _check_production_secrets(self) -> "Settings":
        if self.APP_ENV == "production" and (
            len(self.JWT_SECRET) < 32
            or any(m in self.JWT_SECRET.lower() for m in _WEAK_SECRET_MARKERS)
        ):
            msg = "JWT_SECRET is too weak for production; use 32+ chars"
            raise ValueError(msg)
        return self

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

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

    # Sentry
    SERVER_SENTRY_DSN: str = ""
    SERVER_SENTRY_RELEASE: str = ""

    # Telegram Bot
    TELEGRAM_BOT_TO_DO_TOKEN: str = ""
    TELEGRAM_BOT_CHAT_TOKEN: str = ""
    TELEGRAM_ALLOWED_USER_ID: int = 0
    TIMEZONE: str = "Europe/Amsterdam"

    # Google Calendar
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = ""
    GITHUB_ALLOWED_USERS: Annotated[list[str], NoDecode] = []

    # Donations
    STRIPE_LINK: str = ""
    TELEGRAM_LINK: str = ""
    CRYPTO_BTC_ADDRESS: str = ""
    CRYPTO_ETH_ADDRESS: str = ""

    # Spotify
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    SPOTIFY_REFRESH_TOKEN: str = ""

    # AI provider API keys
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    PERPLEXITY_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost",
        "http://localhost:80",
    ]

    # Seed
    SEED_PASSWORD: str = ""

    # App
    APP_ENV: str = "development"
    APP_NAME: str = "gLOrng"
    BASE_URL: str = "http://localhost"
    MEDIA_DIR: str = "/app/media"


@lru_cache
def get_settings() -> Settings:
    return Settings()
