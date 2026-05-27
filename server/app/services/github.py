"""GitHub OAuth service for code exchange and user info."""

import httpx

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.logging import logger
from app.settings import get_settings

_GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
_GITHUB_USER_URL = "https://api.github.com/user"


async def exchange_code_for_token(code: str) -> str:
    """Exchange an OAuth authorization code for an access token."""
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            _GITHUB_TOKEN_URL,
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )

    if resp.status_code != 200:
        logger.error("GitHub token exchange failed", context={"status": resp.status_code})
        raise UnauthorizedError("Failed to exchange GitHub authorization code")

    data = resp.json()
    token = data.get("access_token")
    if not token:
        error = data.get("error_description", data.get("error", "unknown"))
        logger.error("GitHub token exchange error", context={"error": error})
        raise UnauthorizedError(f"GitHub OAuth error: {error}")

    return token


async def get_github_user(access_token: str) -> dict:
    """Fetch authenticated GitHub user profile."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            _GITHUB_USER_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )

    if resp.status_code != 200:
        logger.error("GitHub user fetch failed", context={"status": resp.status_code})
        raise UnauthorizedError("Failed to fetch GitHub user info")

    return resp.json()


def validate_allowed_user(username: str) -> None:
    """Raise ForbiddenError if username is not in the allow list."""
    settings = get_settings()
    allowed = [u.lower() for u in settings.GITHUB_ALLOWED_USERS]
    if username.lower() not in allowed:
        logger.warning("GitHub user not allowed", context={"username": username})
        raise ForbiddenError(f"GitHub user '{username}' is not authorized")
