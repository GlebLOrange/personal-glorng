"""CSRF helpers for cookie-authenticated API requests."""

from starlette.requests import Request

from app.settings import get_settings

_MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_EXEMPT_PREFIXES = (
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/firebase",
    "/api/auth/forgot-password",
    "/api/auth/reset-password",
    "/api/auth/verify",
    "/api/feedback",
    "/api/auth/github",
)
_ACCESS_COOKIE = "access_token"
_REFRESH_COOKIE = "refresh_token"


def _origin_allowed(request: Request, allowed_origins: list[str]) -> bool:
    origin = request.headers.get("origin")
    if origin and origin in allowed_origins:
        return True
    referer = request.headers.get("referer", "")
    for allowed in allowed_origins:
        if referer == allowed or referer.startswith(f"{allowed}/"):
            return True
    return False


def csrf_origin_rejected(request: Request) -> bool:
    """Return True when a cookie-auth mutating request fails origin checks."""
    settings = get_settings()
    # Skip only for local/unit environments; staging and production enforce CSRF.
    if settings.APP_ENV in {"development", "test"}:
        return False
    if request.method not in _MUTATING_METHODS:
        return False
    path = request.url.path
    if not path.startswith("/api"):
        return False
    if path.startswith("/api/auth/refresh"):
        if _REFRESH_COOKIE not in request.cookies:
            return False
        return not _origin_allowed(request, settings.CORS_ORIGINS)
    if any(path.startswith(prefix) for prefix in _EXEMPT_PREFIXES):
        return False
    if _ACCESS_COOKIE not in request.cookies:
        return False
    return not _origin_allowed(request, settings.CORS_ORIGINS)
