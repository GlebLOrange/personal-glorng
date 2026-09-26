"""Public QR code generator (Segno, rate limited)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import Response

from app.core.deps import OptionalUser
from app.core.rate_limit import rate_limit_api
from app.core.utils import DEFAULT_PER_PAGE
from app.db.deps import DbRegistry
from app.schemas.qr_generator import QrCodeCreate, QrCodeListResponse, QrCodeResponse
from app.services.qr_generator import QrGeneratorService

router = APIRouter(
    prefix="/qr-generator",
    tags=["qr-generator"],
    dependencies=[Depends(rate_limit_api)],
)


@router.post(
    "",
    response_model=QrCodeResponse,
    status_code=201,
    summary="Create QR code",
    description=(
        "Public QR code creation (rate limited). Payload is stored for SVG download."
    ),
)
async def create_qr_code(
    data: QrCodeCreate,
    registry: DbRegistry,
    user: OptionalUser,
) -> QrCodeResponse:
    created_by = user.id if user is not None else None
    svc = QrGeneratorService(registry)
    return await svc.create(data, created_by=created_by)


@router.get(
    "",
    response_model=QrCodeListResponse,
    summary="List recent QR codes",
    description=(
        "Public paginated list of recently created QR codes (preview only)."
    ),
)
async def list_qr_codes(
    registry: DbRegistry,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = DEFAULT_PER_PAGE,
) -> QrCodeListResponse:
    svc = QrGeneratorService(registry)
    return await svc.list_recent(page=page, per_page=per_page)


@router.get(
    "/{qr_id}",
    response_model=QrCodeResponse,
    summary="Get QR code metadata",
)
async def get_qr_code(
    qr_id: Annotated[int, Path(ge=1)],
    registry: DbRegistry,
) -> QrCodeResponse:
    svc = QrGeneratorService(registry)
    return await svc.get_response(qr_id)


@router.get(
    "/{qr_id}/svg",
    summary="Download QR code SVG",
    response_class=Response,
)
async def get_qr_code_svg(
    qr_id: Annotated[int, Path(ge=1)],
    registry: DbRegistry,
) -> Response:
    svc = QrGeneratorService(registry)
    svg = await svc.render_svg(qr_id)
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"},
    )
