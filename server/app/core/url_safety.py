"""URL safety checks for user-supplied redirect targets."""

import ipaddress
import re
from urllib.parse import urlparse

_BLOCKED_HOST_SUFFIXES = (".local", ".localhost", ".internal")
_LOCALHOST_NAMES = frozenset({"localhost", "localhost.localdomain"})


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


def is_safe_redirect_url(url: str) -> bool:
    """Return True when URL is safe for public short-link redirects."""
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

    # Block obvious numeric private ranges without full IP parse (e.g. 192.168.x.x)
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
        return _is_blocked_ip(host)

    return True


def is_public_http_url(url: str) -> bool:
    """Return True when URL is safe enough for server-side HTTP fetching."""
    return is_safe_redirect_url(url)


def validate_redirect_url(url: str) -> str:
    """Validate URL for shortener create; raise ValueError when unsafe."""
    if not is_safe_redirect_url(url):
        msg = "URL is not allowed for shortening"
        raise ValueError(msg)
    return url
