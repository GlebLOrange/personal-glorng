"""URL shortener API.

Create/list/update/delete require `url-shortener` capabilities.
Guest demos use client localStorage instead of anonymous DB rows.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import RedirectResponse

from app.core.deps import AuthorizedUser, UrlServiceDep, require_capability
from app.core.permissions import (
    SUPERUSER_PERMISSION,
    user_has_permission,
)
from app.core.rate_limit import rate_limit_api, rate_limit_shortener_create
from app.core.utils import DEFAULT_PER_PAGE
from app.openapi import requires_capability
from app.schemas.url import UrlCreate, UrlListResponse, UrlResponse, UrlUpdate

router = APIRouter(prefix="/url-shortener", tags=["url-shortener"])


@router.post(
    "",
    response_model=UrlResponse,
    status_code=201,
    summary="Create short URL",
    description=requires_capability("url-shortener", "write"),
    dependencies=[
        Depends(rate_limit_api),
        Depends(rate_limit_shortener_create),
        Depends(require_capability("url-shortener", "write")),
    ],
)
async def create_url(
    data: UrlCreate,
    svc: UrlServiceDep,
    user: AuthorizedUser,
) -> UrlResponse:
    url = await svc.create_short_url(
        original_url=str(data.original_url),
        created_by=user.id,
        title=data.title,
    )
    return UrlResponse.model_validate(url)


@router.get(
    "",
    response_model=UrlListResponse,
    summary="List short URLs",
    description=requires_capability("url-shortener", "read"),
    dependencies=[Depends(require_capability("url-shortener", "read"))],
)
async def list_urls(
    svc: UrlServiceDep,
    user: AuthorizedUser,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = DEFAULT_PER_PAGE,
) -> UrlListResponse:
    return await svc.list_by_owner(created_by=user.id, page=page, per_page=per_page)


@router.patch(
    "/{url_id}",
    response_model=UrlResponse,
    summary="Update short URL",
    description=requires_capability("url-shortener", "write"),
    dependencies=[Depends(require_capability("url-shortener", "write"))],
)
async def update_url(
    url_id: int,
    data: UrlUpdate,
    svc: UrlServiceDep,
    user: AuthorizedUser,
) -> UrlResponse:
    url = await svc.update_url(
        url_id,
        title=data.title,
        actor_id=user.id,
        is_superuser=user_has_permission(user, SUPERUSER_PERMISSION),
    )
    return UrlResponse.model_validate(url)


@router.delete(
    "/{url_id}",
    status_code=204,
    summary="Delete short URL",
    description=requires_capability("url-shortener", "write"),
    dependencies=[Depends(require_capability("url-shortener", "write"))],
)
async def delete_url(
    url_id: int,
    svc: UrlServiceDep,
    user: AuthorizedUser,
) -> None:
    await svc.delete_url(
        url_id,
        actor_id=user.id,
        is_superuser=user_has_permission(user, SUPERUSER_PERMISSION),
    )


redirect_router = APIRouter()


@redirect_router.get(
    "/s/{code}",
    include_in_schema=False,
    dependencies=[Depends(rate_limit_api)],
)
async def redirect_short_url(
    svc: UrlServiceDep,
    code: str = Path(min_length=1, max_length=16, pattern=r"^[a-zA-Z0-9]+$"),
) -> RedirectResponse:
    url = await svc.get_by_code(code)
    await svc.increment_clicks(code)
    return RedirectResponse(url=url.original_url, status_code=307)
