from fastapi import APIRouter

from app.core.deps import (
    AdminUser,
    NewsServiceDep,
)
from app.db.documents.news import NewsSource
from app.schemas.common import MessageResponse
from app.schemas.news import (
    NewsSourceCreate,
    NewsSourceResponse,
    NewsSourcesRefreshRequest,
    NewsSourceUpdate,
)
from app.services.news_ingest import NewsIngestService

router = APIRouter(
    prefix="/news-sources",
    tags=["news"],
)

@router.get(
    "",
    response_model=list[NewsSourceResponse],
    summary="List RSS news sources",
    description="Requires platform superuser.",
)
async def list_news_sources(
    svc: NewsServiceDep,
    user: AdminUser,  # noqa: ARG001
) -> list[NewsSource]:
    """List admin-managed RSS sources."""
    return await svc.list_sources()


@router.post(
    "",
    response_model=NewsSourceResponse,
    summary="Create RSS news source",
    description="Requires platform superuser.",
)
async def create_source(
    data: NewsSourceCreate,
    svc: NewsServiceDep,
    user: AdminUser,
) -> NewsSource:
    """Create an RSS source."""
    return await svc.create_source(data, actor_id=user.id)


@router.post(
    "/refresh",
    response_model=MessageResponse,
    summary="Parse RSS sources into stored news articles",
    description="Requires platform superuser.",
)
async def refresh_sources(
    data: NewsSourcesRefreshRequest,
    svc: NewsServiceDep,
    user: AdminUser,
) -> MessageResponse:
    """Run RSS parsing for enabled sources."""
    result = await NewsIngestService(svc).ingest(
        actor_id=user.id,
        source_ids=data.source_ids,
    )
    return MessageResponse(
        message=(
            "News source refresh completed: "
            f"{result.created} created, {result.skipped} skipped, "
            f"{result.failed} failed"
        )
    )


@router.put(
    "/{source_id}",
    response_model=NewsSourceResponse,
    summary="Update RSS news source",
    description="Requires platform superuser.",
)
async def update_source(
    source_id: int,
    data: NewsSourceUpdate,
    svc: NewsServiceDep,
    user: AdminUser,
) -> NewsSource:
    """Update an RSS source."""
    return await svc.update_source(source_id, data, actor_id=user.id)


@router.delete(
    "/{source_id}",
    response_model=MessageResponse,
    summary="Delete RSS news source",
    description="Requires platform superuser.",
)
async def delete_source(
    source_id: int,
    svc: NewsServiceDep,
    user: AdminUser,
) -> MessageResponse:
    """Delete an RSS source."""
    await svc.delete_source(source_id, actor_id=user.id)
    return MessageResponse(message="News source deleted")
