"""URL safety checks for user-supplied redirect targets and server-side fetches."""

from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urljoin, urlparse

import httpx

_BLOCKED_HOST_SUFFIXES = (".local", ".localhost", ".internal")
_LOCALHOST_NAMES = frozenset({"localhost", "localhost.localdomain"})
_MAX_PUBLIC_REDIRECTS = 5
_HAS_AUTHORITY_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)


def ensure_http_scheme(value: object) -> object:
    """Prepend https:// when there is no scheme (does not invent www)."""
    if not isinstance(value, str):
        return value
    trimmed = value.strip()
    if not trimmed:
        return trimmed
    lower = trimmed.lower()
    if lower.startswith(("http://", "https://")):
        return trimmed
    if trimmed.startswith("//"):
        return f"https:{trimmed}"
    # Leave ftp:// etc. alone so HttpUrl / safety can reject them.
    if _HAS_AUTHORITY_SCHEME.match(trimmed):
        return trimmed
    return f"https://{trimmed}"


def _hostname_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.username or parsed.password:
        return None
    host = parsed.hostname
    if not host:
        return None
    return host.lower().rstrip(".")


def _is_blocked_ip(host: str) -> bool:
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return False
    return bool(
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def _is_syntactically_safe_http_url(
    url: str,
    *,
    allow_public_ip_literals: bool,
) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if parsed.username or parsed.password:
        return False

    host = _hostname_from_url(url)
    if not host:
        return False
    if host in _LOCALHOST_NAMES:
        return False
    if any(host.endswith(suffix) for suffix in _BLOCKED_HOST_SUFFIXES):
        return False
    if _is_blocked_ip(host):
        return False

    # Shortener rejects raw IPv4 literals; fetch path allows public ones.
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
        return allow_public_ip_literals

    return True


def _hostname_resolves_to_blocked(host: str) -> bool:
    """Return True when DNS fails closed or any A/AAAA is non-public."""
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        return _is_blocked_ip(host)

    try:
        results = socket.getaddrinfo(host, None)
    except OSError:
        return True
    if not results:
        return True
    for _family, _type, _proto, _canon, sockaddr in results:
        if not sockaddr:
            continue
        if _is_blocked_ip(str(sockaddr[0])):
            return True
    return False


def is_safe_redirect_url(url: str) -> bool:
    """Return True when URL is safe for public short-link redirects (browser follow)."""
    return _is_syntactically_safe_http_url(url, allow_public_ip_literals=False)


def is_public_http_url(url: str) -> bool:
    """Return True when URL is safe enough for server-side HTTP fetching.

    Includes DNS resolution so names that resolve to private/link-local/reserved
    addresses are rejected (fail closed on DNS errors).
    """
    if not _is_syntactically_safe_http_url(url, allow_public_ip_literals=True):
        return False
    host = _hostname_from_url(url)
    if not host:
        return False
    return not _hostname_resolves_to_blocked(host)


def validate_redirect_url(url: str) -> str:
    """Validate URL for shortener create; raise ValueError when unsafe."""
    if not is_safe_redirect_url(url):
        msg = "URL is not allowed for shortening"
        raise ValueError(msg)
    return url


async def get_public_http_url(
    client: httpx.AsyncClient,
    url: str,
    *,
    max_redirects: int = _MAX_PUBLIC_REDIRECTS,
    **request_kwargs: object,
) -> httpx.Response:
    """GET ``url`` without auto-follow; re-validate every hop including DNS."""
    current = url
    for _ in range(max_redirects + 1):
        if not is_public_http_url(current):
            msg = "URL is not allowed for server-side fetch"
            raise ValueError(msg)
        response = await client.request(
            "GET",
            current,
            follow_redirects=False,
            **request_kwargs,  # type: ignore[arg-type]
        )
        if response.is_redirect:
            location = response.headers.get("location")
            await response.aclose()
            if not location:
                msg = "Redirect missing Location header"
                raise ValueError(msg)
            current = urljoin(str(response.url), location)
            continue
        return response
    msg = "Too many redirects"
    raise ValueError(msg)
