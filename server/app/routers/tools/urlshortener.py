"""URL shortener API. Public create; list/delete require `url-shortener` capabilities."""

from fastapi import APIRouter, Depends, Path
from fastapi.responses import RedirectResponse

from app.core.deps import AuthorizedUser, DbSession, OptionalUser, require_capability
from app.core.permissions import (
    SUPERUSER_PERMISSION,
    permission_key,
    user_has_permission,
)
from app.core.rate_limit import rate_limit_api, rate_limit_shortener_create
from app.core.utils import paginate_params
from app.openapi import requires_capability
from app.schemas.common import MessageResponse
from app.schemas.url import UrlCreate, UrlResponse
from app.services.url import UrlService

router = APIRouter(prefix="/url-shortener", tags=["url-shortener"])


@router.post(
    "",
    response_model=UrlResponse,
    summary="Create short URL",
    description="Public short URL creation (rate limited).",
    dependencies=[
        Depends(rate_limit_api),
        Depends(rate_limit_shortener_create),
    ],
)
async def create_url(
    data: UrlCreate,
    db: DbSession,
    user: OptionalUser,
) -> UrlResponse:
    created_by = (
        user.id
        if user is not None
        and user_has_permission(user, permission_key("url-shortener", "write"))
        else None
    )
    svc = UrlService(db)
    url = await svc.create_short_url(
        original_url=str(data.original_url),
        created_by=created_by,
        title=data.title,
    )
    return UrlResponse.model_validate(url)


@router.get(
    "",
    response_model=list[UrlResponse],
    summary="List short URLs",
    description=requires_capability("url-shortener", "read"),
    dependencies=[Depends(require_capability("url-shortener", "read"))],
)
async def list_urls(
    db: DbSession,
    user: AuthorizedUser,
    page: int = 1,
    per_page: int = 20,
) -> list[UrlResponse]:
    offset, limit = paginate_params(page, per_page)
    svc = UrlService(db)
    urls = await svc.list_by_owner(created_by=user.id, offset=offset, limit=limit)
    return [UrlResponse.model_validate(u) for u in urls]


@router.delete(
    "/{url_id}",
    response_model=MessageResponse,
    summary="Delete short URL",
    description=requires_capability("url-shortener", "write"),
    dependencies=[Depends(require_capability("url-shortener", "write"))],
)
async def delete_url(
    url_id: int,
    db: DbSession,
    user: AuthorizedUser,
) -> MessageResponse:
    svc = UrlService(db)
    await svc.delete_url(
        url_id,
        actor_id=user.id,
        is_superuser=user_has_permission(user, SUPERUSER_PERMISSION),
    )
    return MessageResponse(message="URL deleted")


redirect_router = APIRouter()


@redirect_router.get(
    "/s/{code}",
    include_in_schema=False,
    dependencies=[Depends(rate_limit_api)],
)
async def redirect_short_url(
    db: DbSession,
    code: str = Path(min_length=1, max_length=16, pattern=r"^[a-zA-Z0-9]+$"),
) -> RedirectResponse:
    svc = UrlService(db)
    url = await svc.get_by_code(code)
    await svc.increment_clicks(code)
    return RedirectResponse(url=url.original_url, status_code=307)
