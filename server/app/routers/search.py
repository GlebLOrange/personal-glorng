"""Public portfolio search — keyword lookup and grounded AI chat."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.core.deps import AiSearchServiceDep, AppSettings, SearchIndexServiceDep
from app.core.exceptions import ApiError
from app.core.feature_flags import is_ai_search_enabled
from app.core.rate_limit import RateLimiter
from app.db.documents.search import SearchVisibility
from app.routers.sse import stream_search_sse
from app.schemas.search import (
    SearchChatRequest,
    SearchConfigResponse,
    SearchHit,
    SearchQueryResponse,
)
from app.services.ai_search import SearchScope
from app.services.search_index import SearchIndexService

router = APIRouter(prefix="/search", tags=["search"])

rate_limit_search_chat = RateLimiter(requests=5, window=300)
rate_limit_search_query = RateLimiter(requests=30, window=60)


def _require_ai_search_enabled() -> None:
    if not is_ai_search_enabled():
        raise ApiError(503, "AI search is disabled or not configured")


@router.get(
    "/config",
    response_model=SearchConfigResponse,
    summary="Read public search configuration",
)
async def search_config(settings: AppSettings) -> SearchConfigResponse:
    return SearchConfigResponse(
        enabled=is_ai_search_enabled(),
        configured=bool(settings.GEMINI_API_KEY),
    )


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


@router.post(
    "/chat",
    summary="Stream grounded public search chat",
    description="Public endpoint — searches portfolio content then streams an answer.",
    dependencies=[Depends(rate_limit_search_chat)],
)
async def search_chat(
    body: SearchChatRequest,
    service: AiSearchServiceDep,
) -> StreamingResponse:
    _require_ai_search_enabled()
    messages = [m.model_dump() for m in body.messages]
    return StreamingResponse(
        stream_search_sse(
            service,
            messages,
            scope=SearchScope.PUBLIC,
            error_context="Public search chat stream failed",
        ),
        media_type="text/event-stream",
    )
