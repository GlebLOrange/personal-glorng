from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import NewsServiceDep
from app.core.rate_limit import rate_limit_api
from app.schemas.news import (
    NewsArticleSortField,
    NewsListResponse,
    SortOrder,
)
from app.services.news import DEFAULT_NEWS_PER_PAGE

router = APIRouter(prefix="/news", tags=["news"])


@router.get(
    "",
    response_model=NewsListResponse,
    summary="List public news",
    description="Public news articles loaded from stored feed and curated records.",
    dependencies=[Depends(rate_limit_api)],
)
async def list_news(
    svc: NewsServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[
        int,
        Query(ge=1, le=DEFAULT_NEWS_PER_PAGE),
    ] = DEFAULT_NEWS_PER_PAGE,
    source: Annotated[str | None, Query(max_length=120)] = None,
    category: Annotated[str | None, Query(max_length=64)] = None,
    region: Annotated[str | None, Query(max_length=64)] = None,
    sort_by: NewsArticleSortField = "published_at",
    sort_order: SortOrder = "desc",
) -> NewsListResponse:
    """Return stored public news articles."""
    return await svc.get_public_news(
        page=page,
        per_page=per_page,
        source=source,
        category=category,
        region=region,
        sort_by=sort_by,
        sort_order=sort_order,
    )
