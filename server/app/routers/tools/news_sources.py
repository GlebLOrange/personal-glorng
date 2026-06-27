from fastapi import APIRouter, Depends

from app.core.deps import (
    AuthorizedUser,
    JobQueueDep,
    NewsServiceDep,
    require_capability,
)
from app.core.exceptions import ApiError
from app.db.documents.news import NewsSource
from app.openapi import requires_capability
from app.schemas.common import MessageResponse
from app.schemas.news import (
    NewsSourceCreate,
    NewsSourceResponse,
    NewsSourcesRefreshRequest,
    NewsSourceUpdate,
)
from app.workers.job_names import JobName

router = APIRouter(
    prefix="/news-sources",
    tags=["news"],
    dependencies=[Depends(require_capability("news-sources", "read"))],
)

@router.get(
    "",
    response_model=list[NewsSourceResponse],
    summary="List RSS news sources",
    description=requires_capability("news-sources", "read"),
)
async def list_news_sources(
    svc: NewsServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> list[NewsSource]:
    """List admin-managed RSS sources."""
    return await svc.list_sources()


@router.post(
    "",
    response_model=NewsSourceResponse,
    summary="Create RSS news source",
    description=requires_capability("news-sources", "write"),
    dependencies=[Depends(require_capability("news-sources", "write"))],
)
async def create_source(
    data: NewsSourceCreate,
    svc: NewsServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> NewsSource:
    """Create an RSS source."""
    return await svc.create_source(data.model_dump())


@router.post(
    "/refresh",
    response_model=MessageResponse,
    summary="Parse RSS sources into stored news articles",
    description=requires_capability("news-sources", "write"),
    dependencies=[Depends(require_capability("news-sources", "write"))],
)
async def refresh_sources(
    data: NewsSourcesRefreshRequest,
    svc: NewsServiceDep,
    job_queue: JobQueueDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> MessageResponse:
    """Queue RSS parsing for enabled sources."""
    await svc.ensure_default_sources()
    task_id = await job_queue.enqueue(
        JobName.REFRESH_NEWS_SOURCES,
        data.source_ids,
    )
    if task_id is None:
        raise ApiError(503, "News source refresh could not be queued")
    return MessageResponse(message="News source refresh queued")


@router.put(
    "/{source_id}",
    response_model=NewsSourceResponse,
    summary="Update RSS news source",
    description=requires_capability("news-sources", "write"),
    dependencies=[Depends(require_capability("news-sources", "write"))],
)
async def update_source(
    source_id: int,
    data: NewsSourceUpdate,
    svc: NewsServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> NewsSource:
    """Update an RSS source."""
    payload = data.model_dump(exclude_unset=True)
    return await svc.update_source(source_id, payload)


@router.delete(
    "/{source_id}",
    response_model=MessageResponse,
    summary="Delete RSS news source",
    description=requires_capability("news-sources", "write"),
    dependencies=[Depends(require_capability("news-sources", "write"))],
)
async def delete_source(
    source_id: int,
    svc: NewsServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> MessageResponse:
    """Delete an RSS source."""
    await svc.delete_source(source_id)
    return MessageResponse(message="News source deleted")
