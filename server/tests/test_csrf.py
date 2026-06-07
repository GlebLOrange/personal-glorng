import pytest
from starlette.requests import Request

from app.core.csrf import csrf_origin_rejected
from app.settings import get_settings

_PRODUCTION_ENV = {
    "APP_ENV": "production",
    "ENABLE_MONGODB": "true",
    "MONGODB_URL": "mongodb://localhost:27017",
    "MONGODB_DB": "test_glorng",
    "MONGODB_PASSWORD": "production-mongo-password-ok",
    "POSTGRES_USER": "glorng",
    "POSTGRES_PASSWORD": "prod-test-password-16",
    "POSTGRES_DB": "glorng",
    "REDIS_URL": "redis://:prod-test-redis-password@127.0.0.1:6379/0",
    "RABBITMQ_USER": "glorng",
    "RABBITMQ_PASSWORD": "prod-test-rabbitmq-password",
    "CELERY_BROKER_URL": "amqp://glorng:prod-test-rabbitmq-password@localhost:5672//",
    "JWT_SECRET": "production-jwt-signing-key-for-csrf-tests-only-32chars",
}


def _enable_production(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in _PRODUCTION_ENV.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()


def _build_request(
    *,
    method: str = "POST",
    path: str = "/api/tools/calculator",
    cookies: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
) -> Request:
    header_list: list[tuple[bytes, bytes]] = [(b"host", b"test")]
    if cookies:
        header_list.append(
            (
                b"cookie",
                "; ".join(f"{k}={v}" for k, v in cookies.items()).encode(),
            )
        )
    for key, value in (headers or {}).items():
        header_list.append((key.lower().encode(), value.encode()))
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "path": path,
        "raw_path": path.encode(),
        "root_path": "",
        "scheme": "http",
        "query_string": b"",
        "headers": header_list,
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    return Request(scope)


def test_csrf_rejects_cookie_post_without_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_production(monkeypatch)
    request = _build_request(cookies={"access_token": "token"})
    assert csrf_origin_rejected(request) is True
    get_settings.cache_clear()


def test_csrf_allows_cookie_post_with_matching_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_production(monkeypatch)
    origin = get_settings().CORS_ORIGINS[0]
    request = _build_request(
        cookies={"access_token": "token"},
        headers={"origin": origin},
    )
    assert csrf_origin_rejected(request) is False
    get_settings.cache_clear()


def test_csrf_allows_cookie_post_with_exact_referer_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_production(monkeypatch)
    origin = get_settings().CORS_ORIGINS[0]
    request = _build_request(
        cookies={"access_token": "token"},
        headers={"referer": origin},
    )
    assert csrf_origin_rejected(request) is False
    get_settings.cache_clear()


def test_csrf_skipped_in_development(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    get_settings.cache_clear()
    request = _build_request(cookies={"access_token": "token"})
    assert csrf_origin_rejected(request) is False
    get_settings.cache_clear()
