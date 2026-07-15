"""Admin keyword search over indexed admin content."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import AuthorizedUser, SearchIndexServiceDep, require_capability
from app.core.rate_limit import RateLimiter
from app.db.documents.search import SearchVisibility
from app.schemas.search import SearchHit, SearchQueryResponse
from app.services.search_index import SearchIndexService
from app.services.search_source_types import SearchSourceType

router = APIRouter(
    prefix="/search",
    tags=["search"],
    dependencies=[Depends(require_capability("search", "read"))],
)

ADMIN_SEARCH_LIMIT = 20
ADMIN_SOURCE_TYPES = (
    SearchSourceType.TASK,
    SearchSourceType.EXPENSE,
    SearchSourceType.FEEDBACK,
    SearchSourceType.URL,
)

rate_limit_admin_search = RateLimiter(requests=60, window=60)


@router.get(
    "",
    response_model=SearchQueryResponse,
    summary="Keyword search over admin indexed content",
    dependencies=[Depends(rate_limit_admin_search)],
)
async def search_admin_documents(
    search_svc: SearchIndexServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    q: str = Query(min_length=1, max_length=500),
    source_type: Annotated[
        SearchSourceType | None,
        Query(description="Limit to one indexed admin source type"),
    ] = None,
) -> SearchQueryResponse:
    if source_type:
        source_types = [source_type.value]
    else:
        source_types = [t.value for t in ADMIN_SOURCE_TYPES]
    results = await search_svc.search(
        q,
        visibilities=[SearchVisibility.ADMIN],
        limit=ADMIN_SEARCH_LIMIT,
        source_types=source_types,
    )
    hits = [
        SearchHit(
            id=hit.id,
            title=hit.title,
            url=hit.url,
            source_type=hit.source_type,
            snippet=SearchIndexService.snippet(hit.body),
            visibility=hit.visibility,
        )
        for hit in results
    ]
    return SearchQueryResponse(query=q, hits=hits)
