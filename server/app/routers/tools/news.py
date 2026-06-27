from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import AuthorizedUser, NewsServiceDep, require_capability
from app.db.documents.news import NewsArticle
from app.openapi import requires_capability
from app.schemas.common import MessageResponse
from app.schemas.news import (
    NewsArticleAdminResponse,
    NewsArticleCreate,
    NewsArticleSortField,
    NewsArticleStatus,
    NewsArticleUpdate,
    SortOrder,
)

router = APIRouter(
    prefix="/news",
    tags=["news"],
    dependencies=[Depends(require_capability("news", "read"))],
)

@router.get(
    "",
    response_model=list[NewsArticleAdminResponse],
    summary="List curated news articles",
    description=requires_capability("news", "read"),
)
async def list_admin_news(
    svc: NewsServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    status: Annotated[list[NewsArticleStatus] | None, Query()] = None,
    sort_by: NewsArticleSortField = "published_at",
    sort_order: SortOrder = "desc",
) -> list[NewsArticle]:
    """List admin-curated news articles."""
    return await svc.list_admin_articles(
        statuses=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post(
    "",
    response_model=NewsArticleAdminResponse,
    summary="Create curated news article",
    description=requires_capability("news", "write"),
    dependencies=[Depends(require_capability("news", "write"))],
)
async def create_admin_news(
    data: NewsArticleCreate,
    svc: NewsServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> NewsArticle:
    """Create an admin-curated news article."""
    return await svc.create_article(data.model_dump())


@router.put(
    "/{article_id}",
    response_model=NewsArticleAdminResponse,
    summary="Update curated news article",
    description=requires_capability("news", "write"),
    dependencies=[Depends(require_capability("news", "write"))],
)
async def update_admin_news(
    article_id: int,
    data: NewsArticleUpdate,
    svc: NewsServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> NewsArticle:
    """Update an admin-curated news article."""
    return await svc.update_article(
        article_id,
        data.model_dump(exclude_unset=True),
    )


@router.delete(
    "/{article_id}",
    response_model=MessageResponse,
    summary="Delete curated news article",
    description=requires_capability("news", "write"),
    dependencies=[Depends(require_capability("news", "write"))],
)
async def delete_admin_news(
    article_id: int,
    svc: NewsServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
) -> MessageResponse:
    """Delete an admin-curated news article."""
    await svc.delete_article(article_id)
    return MessageResponse(message="News article deleted")
