"""Public portfolio keyword search."""

from fastapi import APIRouter, Depends, Query

from app.core.deps import SearchIndexServiceDep
from app.core.rate_limit import RateLimiter
from app.db.documents.search import SearchVisibility
from app.schemas.search import SearchHit, SearchQueryResponse
from app.services.search_index import SearchIndexService

router = APIRouter(prefix="/search", tags=["search"])

rate_limit_search_query = RateLimiter(requests=30, window=60)


@router.get(
    "",
    response_model=SearchQueryResponse,
    summary="Keyword search over public indexed content",
    dependencies=[Depends(rate_limit_search_query)],
)
async def search_documents(
    search_svc: SearchIndexServiceDep,
    q: str = Query(min_length=1, max_length=500),
) -> SearchQueryResponse:
    results = await search_svc.search(
        q,
        visibilities=[SearchVisibility.PUBLIC],
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
