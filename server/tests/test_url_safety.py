import pytest

from app.core.url_safety import is_safe_redirect_url, validate_redirect_url


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
