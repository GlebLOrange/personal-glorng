from fastapi import APIRouter, Depends, Path
from fastapi.responses import RedirectResponse

from app.core.deps import AdminUser, DbSession, require_admin
from app.core.rate_limit import rate_limit_api
from app.core.utils import paginate_params
from app.schemas.common import MessageResponse
from app.schemas.url import UrlCreate, UrlResponse
from app.services.url import UrlService

router = APIRouter(prefix="/url-shortener", dependencies=[Depends(require_admin)])


@router.post("", response_model=UrlResponse)
async def create_url(
    data: UrlCreate,
    db: DbSession,
    user: AdminUser,
) -> UrlResponse:
    svc = UrlService(db)
    url = await svc.create_short_url(
        original_url=str(data.original_url),
        created_by=user.id,
        title=data.title,
    )
    return UrlResponse.model_validate(url)


@router.get("", response_model=list[UrlResponse])
async def list_urls(
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 20,
) -> list[UrlResponse]:
    offset, limit = paginate_params(page, per_page)
    svc = UrlService(db)
    urls = await svc.list(offset=offset, limit=limit)
    return [UrlResponse.model_validate(u) for u in urls]


@router.delete("/{url_id}", response_model=MessageResponse)
async def delete_url(
    url_id: int,
    db: DbSession,
    user: AdminUser,  # noqa: ARG001
) -> MessageResponse:
    svc = UrlService(db)
    await svc.delete_url(url_id)
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
