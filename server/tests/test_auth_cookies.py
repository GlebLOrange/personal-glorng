"""Auth cookie flag helpers."""

from app.routers.auth import _cookie_flags
from app.settings import Settings


def test_cookie_secure_in_production() -> None:
    settings = Settings.model_construct(
        APP_ENV="production",
        BASE_URL="http://localhost",
    )
    assert _cookie_flags(settings)["secure"] is True


def test_cookie_secure_on_https_base_url_even_when_not_production() -> None:
    settings = Settings.model_construct(
        APP_ENV="staging",
        BASE_URL="https://staging.example.com",
    )
    assert _cookie_flags(settings)["secure"] is True


def test_cookie_not_secure_on_local_http_dev() -> None:
    settings = Settings.model_construct(
        APP_ENV="development",
        BASE_URL="http://localhost:3000",
    )
    assert _cookie_flags(settings)["secure"] is False
