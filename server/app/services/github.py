"""GitHub OAuth service for code exchange and user info."""

from typing import Any

import httpx

from app.core.exceptions import ApiError, ForbiddenError, UnauthorizedError
from app.core.logging import logger
from app.schemas.github import GitHubIssueResponse, GitHubRepoResponse
from app.settings import get_settings

_GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
_GITHUB_USER_URL = "https://api.github.com/user"
_GITHUB_REPOS_URL = "https://api.github.com/user/repos"
_GITHUB_ISSUES_URL = "https://api.github.com/issues"
_GITHUB_USER_REPOS_URL = "https://api.github.com/users/{username}/repos"
_DEFAULT_REPO_SORT = "updated"
_DEFAULT_REPO_PER_PAGE = 30
_DEFAULT_TIMEOUT = 20.0


async def exchange_code_for_token(code: str) -> str:
    """Exchange an OAuth authorization code for an access token."""
    settings = get_settings()

    async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT) as client:
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
        logger.error(
            "GitHub token exchange failed",
            context={"status": resp.status_code},
        )
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
    async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT) as client:
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


def _github_headers(access_token: str | None = None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def _map_repo(item: dict[str, Any]) -> GitHubRepoResponse:
    return GitHubRepoResponse(
        name=item["name"],
        full_name=item["full_name"],
        html_url=item["html_url"],
        description=item.get("description"),
        language=item.get("language"),
        stargazers_count=int(item.get("stargazers_count", 0)),
        fork=bool(item.get("fork", False)),
        private=bool(item.get("private", False)),
        updated_at=item.get("updated_at"),
    )


def _map_issue(item: dict[str, Any]) -> GitHubIssueResponse:
    repo = item.get("repository") or {}
    return GitHubIssueResponse(
        number=int(item["number"]),
        title=item["title"],
        html_url=item["html_url"],
        state=item["state"],
        repository=str(repo.get("full_name", "")),
        created_at=item["created_at"],
        updated_at=item["updated_at"],
    )


async def _fetch_github_json(
    url: str,
    *,
    access_token: str | None = None,
    params: dict[str, str | int] | None = None,
) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT) as client:
        resp = await client.get(
            url,
            headers=_github_headers(access_token),
            params=params,
        )

    if resp.status_code == 401:
        raise UnauthorizedError("GitHub token is invalid or expired")
    if resp.status_code == 403:
        raise ApiError(502, "GitHub API rate limit or access denied")
    if resp.status_code != 200:
        logger.error(
            "GitHub API request failed",
            context={"url": url, "status": resp.status_code},
        )
        raise ApiError(502, "GitHub API request failed")

    data = resp.json()
    if not isinstance(data, list):
        msg = "Expected a list response from GitHub"
        raise TypeError(msg)
    return data


async def list_user_repos(access_token: str) -> list[GitHubRepoResponse]:
    """List repositories for the authenticated GitHub user."""
    raw = await _fetch_github_json(
        _GITHUB_REPOS_URL,
        access_token=access_token,
        params={
            "sort": _DEFAULT_REPO_SORT,
            "per_page": _DEFAULT_REPO_PER_PAGE,
            "affiliation": "owner",
        },
    )
    return [_map_repo(item) for item in raw if not item.get("fork")]


async def list_assigned_issues(access_token: str) -> list[GitHubIssueResponse]:
    """List open issues assigned to the authenticated GitHub user."""
    raw = await _fetch_github_json(
        _GITHUB_ISSUES_URL,
        access_token=access_token,
        params={"filter": "assigned", "state": "open", "per_page": 20},
    )
    return [_map_issue(item) for item in raw if "pull_request" not in item]


async def list_public_repos(username: str) -> list[GitHubRepoResponse]:
    """List public repositories for a GitHub username (no OAuth token)."""
    url = _GITHUB_USER_REPOS_URL.format(username=username)
    raw = await _fetch_github_json(
        url,
        params={"sort": _DEFAULT_REPO_SORT, "per_page": _DEFAULT_REPO_PER_PAGE},
    )
    public = [
        item
        for item in raw
        if not item.get("fork") and not item.get("private", False)
    ]
    return [_map_repo(item) for item in public]
