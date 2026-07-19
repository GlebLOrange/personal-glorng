"""Unit tests for rate-limit client IP extraction."""

from starlette.requests import Request

from app.core.rate_limit import client_ip


def _request_with_headers(headers: dict[str, str], client_host: str | None = "127.0.0.1") -> Request:
    scope: dict = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "client": (client_host, 12345) if client_host else None,
        "server": ("test", 80),
    }
    return Request(scope)


def test_client_ip_prefers_x_real_ip() -> None:
    """nginx-set X-Real-IP wins over the socket peer (Cloudflare POP or local)."""
    request = _request_with_headers({"x-real-ip": "203.0.113.50"}, client_host="10.0.0.1")
    assert client_ip(request) == "203.0.113.50"


def test_client_ip_falls_back_to_peer() -> None:
    request = _request_with_headers({}, client_host="192.0.2.10")
    assert client_ip(request) == "192.0.2.10"


def test_client_ip_unknown_without_peer() -> None:
    request = _request_with_headers({}, client_host=None)
    request.scope["client"] = None
    assert client_ip(request) == "unknown"
