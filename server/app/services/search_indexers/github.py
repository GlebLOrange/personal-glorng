"""GitHub repository search indexing."""

from app.db.documents.search import SearchVisibility
from app.db.registry import DatabaseRegistry
from app.schemas.github import GitHubRepoResponse
from app.services.search_index import SearchIndexService
from app.services.search_source_types import SearchSourceType
from app.services.search_types import SearchDocumentInput

GITHUB_SOURCE_TYPE = SearchSourceType.RESUME


async def index_github_repos(
    registry: DatabaseRegistry,
    *,
    _username: str,
    repos: list[GitHubRepoResponse],
) -> int:
    """Upsert public GitHub repos into the search index."""
    svc = SearchIndexService(registry)
    keep_ids = set(range(1, len(repos) + 1))
    await svc.delete_stale_by_source(GITHUB_SOURCE_TYPE, keep_ids)

    for index, repo in enumerate(repos, start=1):
        body_parts = [
            repo.description or "",
            repo.language or "",
            repo.html_url,
        ]
        await svc.upsert(
            SearchDocumentInput(
                source_type=GITHUB_SOURCE_TYPE,
                source_id=300 + index,
                title=f"GitHub: {repo.full_name}",
                body="\n".join(part for part in body_parts if part),
                url=repo.html_url,
                visibility=SearchVisibility.PUBLIC,
            ),
        )
    return len(repos)
