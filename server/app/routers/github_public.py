"""Public GitHub API endpoints."""

from fastapi import APIRouter, Depends

from app.core.deps import AppSettings
from app.core.exceptions import NotFoundError
from app.core.rate_limit import rate_limit_api
from app.db.deps import DbRegistry
from app.schemas.github import GitHubRepoResponse
from app.services.github_portfolio import get_public_github_repos

router = APIRouter(dependencies=[Depends(rate_limit_api)])


@router.get(
    "/repos",
    response_model=list[GitHubRepoResponse],
    summary="Public GitHub repositories",
    description=(
        "List public repositories for GITHUB_PUBLIC_USERNAME "
        "(or the first GITHUB_ALLOWED_USERS entry)."
    ),
)
async def public_github_repos(
    registry: DbRegistry,
    settings: AppSettings,
) -> list[GitHubRepoResponse]:
    username, repos = await get_public_github_repos(settings, registry=registry)
    if not username:
        raise NotFoundError("Public GitHub username is not configured")
    return repos
