import pytest
from starlette.requests import Request

from app.core.csrf import csrf_origin_rejected
from app.settings import get_settings


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
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()
    request = _build_request(cookies={"access_token": "token"})
    assert csrf_origin_rejected(request) is True
    get_settings.cache_clear()


def test_csrf_allows_cookie_post_with_matching_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()
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
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()
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
