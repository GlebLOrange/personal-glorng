"""Curated news API. Public reads; writes require `news:write`."""

from fastapi import APIRouter, Depends

from app.core.deps import AdminUser, NewsServiceDep
from app.core.rate_limit import rate_limit_api
from app.db.documents.news import NewsStatus
from app.schemas.common import MessageResponse
from app.schemas.news import (
    NewsArticleCreate,
    NewsArticleListResponse,
    NewsArticleMetadataRequest,
    NewsArticleMetadataResponse,
    NewsArticleResponse,
    NewsArticleUpdate,
    NewsIngestResponse,
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
    page: int = 1,
    per_page: int = 20,
) -> NewsArticleListResponse:
    """List published news articles."""
    return await svc.list_articles(
        status="published",
        page=page,
        per_page=per_page,
    )


@router.get(
    "/admin",
    response_model=NewsArticleListResponse,
    summary="List news for admin",
    description="Requires platform superuser.",
)
async def list_news_admin(
    svc: NewsServiceDep,
    user: AdminUser,
    status: NewsStatus | None = None,
    page: int = 1,
    per_page: int = 20,
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
    description="Requires platform superuser.",
)
async def load_article_metadata(
    data: NewsArticleMetadataRequest,
    svc: NewsServiceDep,
    user: AdminUser,
) -> NewsArticleMetadataResponse:
    """Load article metadata from a public URL."""
    return await svc.load_article_metadata(str(data.url), actor_id=user.id)


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
    summary="Create news article",
    description="Requires platform superuser.",
)
async def create_news_article(
    data: NewsArticleCreate,
    svc: NewsServiceDep,
    user: AdminUser,
) -> NewsArticleResponse:
    """Create a news article manually."""
    return await svc.create_article(data, actor_id=user.id)


@router.post(
    "/ingest",
    response_model=NewsIngestResponse,
    summary="Run news ingestion",
    description="Requires platform superuser.",
)
async def ingest_news(
    svc: NewsServiceDep,
    user: AdminUser,
) -> NewsIngestResponse:
    """Run a news ingestion pass."""
    from app.services.news_ingest import NewsIngestService

    return await NewsIngestService(svc).ingest(actor_id=user.id)


@router.post(
    "/{article_id}/telegram",
    response_model=NewsArticleResponse,
    summary="Publish news article to Telegram",
    description="Requires platform superuser.",
)
async def publish_news_to_telegram(
    article_id: int,
    svc: NewsServiceDep,
    user: AdminUser,
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
    description="Requires platform superuser.",
)
async def update_news_article(
    article_id: int,
    data: NewsArticleUpdate,
    svc: NewsServiceDep,
    user: AdminUser,
) -> NewsArticleResponse:
    """Update a news article."""
    return await svc.update_article(article_id, data, actor_id=user.id)


@router.delete(
    "/{article_id}",
    response_model=MessageResponse,
    summary="Delete news article",
    description="Requires platform superuser.",
)
async def delete_news_article(
    article_id: int,
    svc: NewsServiceDep,
    user: AdminUser,
) -> MessageResponse:
    """Delete a news article."""
    await svc.delete_article(article_id, actor_id=user.id)
    return MessageResponse(message="News article deleted")
