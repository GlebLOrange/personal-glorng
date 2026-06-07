"""GitHub OAuth endpoints for repo access."""

import secrets
from urllib.parse import urlencode

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.core.deps import CurrentUser
from app.core.exceptions import UnauthorizedError
from app.core.logging import logger
from app.core.redis import cache_delete, cache_get, cache_set
from app.db.deps import DbRegistry
from app.db.documents.credential import GitHubCredential
from app.services.github import (
    exchange_code_for_token,
    get_github_user,
    validate_allowed_user,
)
from app.services.github_credentials import store_github_access_token
from app.settings import get_settings

router = APIRouter()

_GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
_STATE_TTL_SECONDS = 600


def _github_oauth_state_key(*, user_public_id: str) -> str:
    return f"oauth:github:state:{user_public_id}"


class GitHubCallbackRequest(BaseModel):
    code: str
    state: str


class GitHubCallbackResponse(BaseModel):
    github_username: str
    message: str


class GitHubStatusResponse(BaseModel):
    linked: bool
    github_username: str | None = None


@router.get(
    "/status",
    response_model=GitHubStatusResponse,
    summary="GitHub link status",
)
async def github_status(
    user: CurrentUser, registry: DbRegistry
) -> GitHubStatusResponse:
    if registry.credentials is None:
        msg = "Credential repository is not initialized"
        raise RuntimeError(msg)

    credential = await registry.credentials.get_github_for_user(user.id)
    if not credential:
        return GitHubStatusResponse(linked=False)
    return GitHubStatusResponse(
        linked=True,
        github_username=credential.github_username,
    )


@router.delete(
    "",
    summary="Unlink GitHub account",
)
async def github_unlink(
    user: CurrentUser, registry: DbRegistry
) -> GitHubStatusResponse:
    if registry.credentials is None:
        msg = "Credential repository is not initialized"
        raise RuntimeError(msg)

    await registry.credentials.delete_github_for_user(user.id)
    logger.info("GitHub account unlinked", context={"user_id": user.id})
    return GitHubStatusResponse(linked=False)


@router.get(
    "/authorize",
    summary="Start GitHub OAuth",
    description="Redirect the authenticated user to GitHub OAuth consent screen.",
)
async def github_authorize(user: CurrentUser) -> RedirectResponse:
    settings = get_settings()
    state = secrets.token_urlsafe(32)
    await cache_set(
        _github_oauth_state_key(user_public_id=str(user.public_id)),
        state,
        ttl=_STATE_TTL_SECONDS,
    )

    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "repo",
        "state": state,
    }

    logger.info(
        "GitHub OAuth initiated",
        context={"user_id": user.id},
    )

    url = f"{_GITHUB_AUTHORIZE_URL}?{urlencode(params)}"
    return RedirectResponse(url=url, status_code=302)


@router.post(
    "/callback",
    response_model=GitHubCallbackResponse,
    summary="Complete GitHub OAuth",
    description="Exchange OAuth code for access token and store credential.",
)
async def github_callback(
    body: GitHubCallbackRequest,
    user: CurrentUser,
    registry: DbRegistry,
) -> GitHubCallbackResponse:
    if registry.credentials is None:
        msg = "Credential repository is not initialized"
        raise RuntimeError(msg)

    state_key = _github_oauth_state_key(user_public_id=str(user.public_id))
    expected_state = await cache_get(state_key)
    if not expected_state or expected_state != body.state:
        logger.warning("GitHub OAuth state mismatch", context={"user_id": user.id})
        raise UnauthorizedError("GitHub OAuth verification failed. Please retry.")

    await cache_delete(state_key)

    access_token = await exchange_code_for_token(body.code)
    gh_user = await get_github_user(access_token)

    username = gh_user["login"]
    github_user_id = gh_user["id"]

    validate_allowed_user(username)

    existing = await registry.credentials.get_github_for_user(user.id)
    encrypted_token = store_github_access_token(access_token)

    if existing:
        existing.access_token = encrypted_token
        existing.github_user_id = github_user_id
        existing.github_username = username
        cred = await registry.credentials.upsert_github(existing)
    else:
        cred = GitHubCredential(
            user_id=user.id,
            github_user_id=github_user_id,
            github_username=username,
            access_token=encrypted_token,
        )
        cred = await registry.credentials.upsert_github(cred)

    logger.info(
        "GitHub account linked",
        context={"user_id": user.id, "github_username": cred.github_username},
    )

    return GitHubCallbackResponse(
        github_username=username,
        message="GitHub account linked successfully",
    )
