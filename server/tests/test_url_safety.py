from unittest.mock import patch

import pytest

from app.core.url_safety import (
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
