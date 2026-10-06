import asyncio
from unittest.mock import patch

import httpx
import pytest

from app.core import url_safety as url_safety_mod
from app.core.url_safety import (
    ensure_http_scheme,
    get_public_http_url,
    is_public_http_url,
    is_safe_redirect_url,
    validate_redirect_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/path",
        "http://example.org",
    ],
)
def test_safe_public_urls(url: str) -> None:
    assert is_safe_redirect_url(url) is True
    assert validate_redirect_url(url) == url


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/admin",
        "https://127.0.0.1/internal",
        "https://192.168.1.1/dashboard",
        "https://10.0.0.5/resource",
        "https://user:pass@example.com",
        "ftp://example.com/file",
    ],
)
def test_unsafe_urls(url: str) -> None:
    assert is_safe_redirect_url(url) is False
    with pytest.raises(ValueError, match="not allowed"):
        validate_redirect_url(url)


def test_public_http_url_rejects_dns_to_private_ip() -> None:
    private = ("127.0.0.1", 0)

    with patch(
        "app.core.url_safety.socket.getaddrinfo",
        return_value=[(None, None, None, None, private)],
    ):
        assert is_public_http_url("https://evil.example/path") is False


def test_public_http_url_allows_dns_to_public_ip() -> None:
    public = ("93.184.216.34", 0)

    with patch(
        "app.core.url_safety.socket.getaddrinfo",
        return_value=[(None, None, None, None, public)],
    ):
        assert is_public_http_url("https://example.com/path") is True


def test_public_http_url_fails_closed_on_dns_error() -> None:
    with patch(
        "app.core.url_safety.socket.getaddrinfo",
        side_effect=OSError("dns down"),
    ):
        assert is_public_http_url("https://example.com/path") is False


def test_shortener_safety_does_not_require_dns() -> None:
    """Browser redirects stay syntactic-only so flaky DNS cannot block create."""
    with patch(
        "app.core.url_safety.socket.getaddrinfo",
        side_effect=OSError("dns down"),
    ):
        assert is_safe_redirect_url("https://example.com/path") is True


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("example.com/path", "https://example.com/path"),
        ("http://example.com", "http://example.com"),
        ("https://example.com", "https://example.com"),
        ("//cdn.example.com/a", "https://cdn.example.com/a"),
        ("ftp://example.com/file", "ftp://example.com/file"),
        ("  ", ""),
        (42, 42),
    ],
)
def test_ensure_http_scheme(raw: object, expected: object) -> None:
    assert ensure_http_scheme(raw) == expected


@pytest.mark.asyncio
async def test_get_public_http_url_sni_and_relative_redirect() -> None:
    """IP connect keeps SNI/host; relative Location joins the pre-rewrite URL."""
    public = ("93.184.216.34", 0)
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if len(seen) == 1:
            return httpx.Response(302, headers={"location": "/final"}, request=request)
        return httpx.Response(200, text="ok", request=request)

    transport = httpx.MockTransport(handler)
    real_to_thread = asyncio.to_thread
    to_thread_calls: list[object] = []

    async def tracking_to_thread(
        func: object, /, *args: object, **kwargs: object
    ) -> object:
        to_thread_calls.append(func)
        return await real_to_thread(func, *args, **kwargs)  # type: ignore[arg-type]

    with (
        patch(
            "app.core.url_safety.socket.getaddrinfo",
            return_value=[(None, None, None, None, public)],
        ),
        patch("app.core.url_safety.asyncio.to_thread", side_effect=tracking_to_thread),
    ):
        async with httpx.AsyncClient(transport=transport) as client:
            response = await get_public_http_url(client, "https://example.com/start")

    assert response.status_code == 200
    assert len(seen) == 2
    assert seen[0].url.host == "93.184.216.34"
    assert seen[0].headers["Host"] == "example.com"
    assert seen[0].extensions.get("sni_hostname") == "example.com"
    assert str(seen[1].url) == "https://93.184.216.34/final"
    assert seen[1].headers["Host"] == "example.com"
    assert seen[1].extensions.get("sni_hostname") == "example.com"
    assert len(to_thread_calls) == 2
    assert all(
        fn is url_safety_mod._resolve_public_ip_for_host for fn in to_thread_calls
    )
