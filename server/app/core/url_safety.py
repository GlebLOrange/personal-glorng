"""URL safety checks for user-supplied redirect targets and server-side fetches."""

from __future__ import annotations

import asyncio
import ipaddress
import re
import socket
from urllib.parse import urljoin, urlparse, urlunparse

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


def _resolve_public_ip_for_host(host: str) -> str | None:
    """Resolve host and return a public IP only when all answers are public."""
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        return None if _is_blocked_ip(host) else host

    try:
        results = socket.getaddrinfo(host, None)
    except OSError:
        return None
    if not results:
        return None

    public_ips: list[str] = []
    for _family, _type, _proto, _canon, sockaddr in results:
        if not sockaddr:
            continue
        ip = str(sockaddr[0])
        if _is_blocked_ip(ip):
            return None
        public_ips.append(ip)

    if not public_ips:
        return None
    return public_ips[0]


def _url_with_ip_host(url: str, ip: str) -> str:
    parsed = urlparse(url)
    if parsed.port is None:
        netloc = ipaddress.ip_address(ip).compressed
    else:
        netloc = f"{ipaddress.ip_address(ip).compressed}:{parsed.port}"
    if ":" in ip and not netloc.startswith("["):
        # Ensure IPv6 literals are bracketed in URL authority.
        netloc = f"[{ip}]" if parsed.port is None else f"[{ip}]:{parsed.port}"
    return urlunparse(
        (
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


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
    """GET ``url`` without auto-follow; re-validate every hop including DNS.

    Connects to a resolved public IP while keeping Host and TLS SNI on the
    original hostname. Redirect Location values are joined against the
    pre-rewrite URL so relative hops keep that host.
    """
    current = url
    for _ in range(max_redirects + 1):
        if not _is_syntactically_safe_http_url(current, allow_public_ip_literals=True):
            msg = "URL is not allowed for server-side fetch"
            raise ValueError(msg)

        host = _hostname_from_url(current)
        if not host:
            msg = "URL is not allowed for server-side fetch"
            raise ValueError(msg)

        # One blocking DNS lookup off the event loop per hop.
        resolved_ip = await asyncio.to_thread(_resolve_public_ip_for_host, host)
        if not resolved_ip:
            msg = "URL is not allowed for server-side fetch"
            raise ValueError(msg)

        parsed_current = urlparse(current)
        connect_url = _url_with_ip_host(current, resolved_ip)

        headers = dict(request_kwargs.get("headers", {}) or {})
        host_header = (
            host if parsed_current.port is None else f"{host}:{parsed_current.port}"
        )
        headers["Host"] = host_header

        request_args = dict(request_kwargs)
        request_args["headers"] = headers
        # Preserve TLS cert verification against the hostname, not the IP.
        existing_extensions = dict(request_args.get("extensions") or {})  # type: ignore[arg-type]
        existing_extensions["sni_hostname"] = host
        request_args["extensions"] = existing_extensions

        response = await client.request(
            "GET",
            connect_url,
            follow_redirects=False,
            **request_args,  # type: ignore[arg-type]
        )
        if response.is_redirect:
            location = response.headers.get("location")
            await response.aclose()
            if not location:
                msg = "Redirect missing Location header"
                raise ValueError(msg)
            # Join against the pre-rewrite URL — response.url is the IP connect URL.
            current = urljoin(current, location)
            continue
        return response
    msg = "Too many redirects"
    raise ValueError(msg)
