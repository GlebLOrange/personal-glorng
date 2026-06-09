"""Cached public GitHub repo listing for portfolio surfaces."""

import json

from app.core.cache_json import safe_cache_json_loads
from app.core.logging import logger
from app.core.redis import cache_get, cache_set
from app.db.registry import DatabaseRegistry
from app.schemas.github import GitHubRepoResponse
from app.services.github import list_public_repos
from app.services.search_indexers.github import index_github_repos
from app.settings import Settings, get_settings

_CACHE_TTL_SECONDS = 300
_CACHE_PREFIX = "github:public-repos:"


async def get_public_github_repos(
    settings: Settings | None = None,
    *,
    registry: DatabaseRegistry | None = None,
) -> tuple[str | None, list[GitHubRepoResponse]]:
    """Return username and repos, using Redis cache when available."""
    active = settings or get_settings()
    username = active.github_public_username()
    if not username:
        return None, []

    cache_key = f"{_CACHE_PREFIX}{username.lower()}"
    cached = await cache_get(cache_key)
    if cached:
        raw = safe_cache_json_loads(cached)
        if isinstance(raw, list):
            return username, [GitHubRepoResponse.model_validate(item) for item in raw]

    repos = await list_public_repos(username)
    await cache_set(
        cache_key,
        json.dumps([repo.model_dump() for repo in repos]),
        ttl=_CACHE_TTL_SECONDS,
    )

    if registry is not None and repos:
        try:
            await index_github_repos(registry, _username=username, repos=repos)
        except Exception as exc:
            logger.warning(
                "GitHub search indexing failed",
                error=exc,
                context={"username": username},
            )

    return username, repos
