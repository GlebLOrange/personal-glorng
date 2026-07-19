"""Curated news API. Public reads; admin routes use news capabilities."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import AuthorizedUser, NewsServiceDep, require_capability
from app.core.rate_limit import rate_limit_api
from app.core.utils import DEFAULT_PER_PAGE
from app.db.documents.news import NewsStatus
from app.openapi import requires_capability
from app.schemas.news import (
    NewsArticleCreate,
    NewsArticleListResponse,
    NewsArticleMetadataRequest,
    NewsArticleMetadataResponse,
    NewsArticleResponse,
    NewsArticleUpdate,
    NewsIngestResponse,
    NewsStatsResponse,
)

router = APIRouter(prefix="/news", tags=["news"])


@router.get(
    "",
    response_model=NewsArticleListResponse,
    summary="List news",
    description="Public curated news list (rate limited).",
    dependencies=[Depends(rate_limit_api)],
)
async def list_news(
    svc: NewsServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = DEFAULT_PER_PAGE,
) -> NewsArticleListResponse:
    """List published news articles."""
    return await svc.list_articles(
        status="published",
        page=page,
        per_page=per_page,
    )


@router.get(
    "/admin/stats",
    response_model=NewsStatsResponse,
    summary="Get news article stats",
    description=requires_capability("news", "read"),
    dependencies=[Depends(require_capability("news", "read"))],
)
async def get_news_stats(
    svc: NewsServiceDep,
    user: AuthorizedUser,
) -> NewsStatsResponse:
    """Return article counts by status for admin tools."""
    del user
    return await svc.news_stats()


@router.get(
    "/admin",
    response_model=NewsArticleListResponse,
    summary="List news for admin",
    description=requires_capability("news", "read"),
    dependencies=[Depends(require_capability("news", "read"))],
)
async def list_news_admin(
    svc: NewsServiceDep,
    user: AuthorizedUser,
    status: NewsStatus | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = DEFAULT_PER_PAGE,
) -> NewsArticleListResponse:
    """List news articles for admin tools."""
    del user
    return await svc.list_articles(
        status=status,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/themes",
    response_model=list[str],
    summary="List news themes",
    description="Public news themes (rate limited).",
    dependencies=[Depends(rate_limit_api)],
)
async def list_news_themes(svc: NewsServiceDep) -> list[str]:
    """List public news themes."""
    return await svc.list_themes()


@router.post(
    "/metadata",
    response_model=NewsArticleMetadataResponse,
    summary="Load article metadata",
    description=requires_capability("news", "write"),
    dependencies=[Depends(require_capability("news", "write"))],
)
async def load_article_metadata(
    data: NewsArticleMetadataRequest,
    svc: NewsServiceDep,
    user: AuthorizedUser,
) -> NewsArticleMetadataResponse:
    """Load article metadata from a public URL."""
    return await svc.load_article_metadata(str(data.url), actor_id=user.id)


@router.get(
    "/admin/{article_id}",
    response_model=NewsArticleResponse,
    summary="Get news article for admin",
    description=requires_capability("news", "read"),
    dependencies=[Depends(require_capability("news", "read"))],
)
async def get_news_article_admin(
    article_id: int,
    svc: NewsServiceDep,
    user: AuthorizedUser,
) -> NewsArticleResponse:
    """Get any news article by ID for admin tools."""
    del user
    return await svc.get_article(article_id)


@router.get(
    "/{slug}",
    response_model=NewsArticleResponse,
    summary="Get news article",
    description="Public news detail (rate limited).",
    dependencies=[Depends(rate_limit_api)],
)
async def get_news_article(slug: str, svc: NewsServiceDep) -> NewsArticleResponse:
    """Get a published news article by slug."""
    return await svc.get_public_article(slug)


@router.post(
    "",
    response_model=NewsArticleResponse,
    status_code=201,
    summary="Create news article",
    description=requires_capability("news", "write"),
    dependencies=[Depends(require_capability("news", "write"))],
)
async def create_news_article(
    data: NewsArticleCreate,
    svc: NewsServiceDep,
    user: AuthorizedUser,
) -> NewsArticleResponse:
    """Create a news article manually."""
    return await svc.create_article(data, actor_id=user.id)


@router.post(
    "/ingest",
    response_model=NewsIngestResponse,
    summary="Run news ingestion",
    description=requires_capability("news", "write"),
    dependencies=[Depends(require_capability("news", "write"))],
)
async def ingest_news(
    svc: NewsServiceDep,
    user: AuthorizedUser,
) -> NewsIngestResponse:
    """Run a news ingestion pass."""
    from app.services.news_ingest import NewsIngestService

    return await NewsIngestService(svc).ingest(actor_id=user.id)


@router.post(
    "/{article_id}/telegram",
    response_model=NewsArticleResponse,
    summary="Publish news article to Telegram",
    description=requires_capability("news", "write"),
    dependencies=[Depends(require_capability("news", "write"))],
)
async def publish_news_to_telegram(
    article_id: int,
    svc: NewsServiceDep,
    user: AuthorizedUser,
) -> NewsArticleResponse:
    """Publish an article to the configured Telegram channel."""
    del user
    from app.services.news_telegram import publish_news_article_to_telegram

    article = await svc.require_article(article_id)
    message_id = await publish_news_article_to_telegram(article)
    return await svc.set_telegram_message_id(article_id, message_id)


@router.put(
    "/{article_id}",
    response_model=NewsArticleResponse,
    summary="Update news article",
    description=requires_capability("news", "write"),
    dependencies=[Depends(require_capability("news", "write"))],
)
async def update_news_article(
    article_id: int,
    data: NewsArticleUpdate,
    svc: NewsServiceDep,
    user: AuthorizedUser,
) -> NewsArticleResponse:
    """Update a news article."""
    return await svc.update_article(article_id, data, actor_id=user.id)


@router.delete(
    "/{article_id}",
    status_code=204,
    summary="Delete news article",
    description=requires_capability("news", "write"),
    dependencies=[Depends(require_capability("news", "write"))],
)
async def delete_news_article(
    article_id: int,
    svc: NewsServiceDep,
    user: AuthorizedUser,
) -> None:
    """Delete a news article."""
    await svc.delete_article(article_id, actor_id=user.id)
