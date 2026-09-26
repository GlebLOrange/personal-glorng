"""Public QR generator (ephemeral) + admin library (persisted SVGs)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import Response

from app.core.deps import AuthorizedUser, require_capability
from app.core.permissions import SUPERUSER_PERMISSION, user_has_permission
from app.core.rate_limit import rate_limit_api
from app.core.utils import DEFAULT_PER_PAGE
from app.db.deps import DbRegistry
from app.openapi import requires_capability
from app.schemas.qr_generator import (
    QrCodeCreate,
    QrCodeGenerateResponse,
    QrCodeListResponse,
    QrCodeStoredResponse,
    QrCodeUpdate,
)
from app.services.qr_generator import QrLibraryService, generate_qr

router = APIRouter(
    prefix="/qr-generator",
    tags=["qr-generator"],
    dependencies=[Depends(rate_limit_api)],
)


@router.post(
    "",
    response_model=QrCodeGenerateResponse,
    status_code=200,
    summary="Generate QR code",
    description=(
        "Public QR generation (rate limited). Inline SVG in JSON; payload not stored."
    ),
)
async def generate_qr_code(data: QrCodeCreate) -> QrCodeGenerateResponse:
    return generate_qr(data)


@router.get(
    "/library",
    response_model=QrCodeListResponse,
    summary="List saved QR codes",
    description=requires_capability("qr-generator", "read"),
    dependencies=[Depends(require_capability("qr-generator", "read"))],
)
async def list_saved_qr_codes(
    registry: DbRegistry,
    user: AuthorizedUser,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = DEFAULT_PER_PAGE,
) -> QrCodeListResponse:
    svc = QrLibraryService(registry)
    return await svc.list_library(
        actor_id=user.id,
        is_superuser=user_has_permission(user, SUPERUSER_PERMISSION),
        page=page,
        per_page=per_page,
    )


@router.post(
    "/library",
    response_model=QrCodeStoredResponse,
    status_code=201,
    summary="Save QR code to library",
    description=requires_capability("qr-generator", "write"),
    dependencies=[Depends(require_capability("qr-generator", "write"))],
)
async def create_saved_qr_code(
    data: QrCodeCreate,
    registry: DbRegistry,
    user: AuthorizedUser,
) -> QrCodeStoredResponse:
    svc = QrLibraryService(registry)
    return await svc.create_saved(data, created_by=user.id)


@router.get(
    "/library/{qr_id}",
    response_model=QrCodeStoredResponse,
    summary="Get saved QR code",
    description=requires_capability("qr-generator", "read"),
    dependencies=[Depends(require_capability("qr-generator", "read"))],
)
async def get_saved_qr_code(
    qr_id: Annotated[int, Path(ge=1)],
    registry: DbRegistry,
    user: AuthorizedUser,
) -> QrCodeStoredResponse:
    svc = QrLibraryService(registry)
    return await svc.get_stored(
        qr_id,
        actor_id=user.id,
        is_superuser=user_has_permission(user, SUPERUSER_PERMISSION),
    )


@router.patch(
    "/library/{qr_id}",
    response_model=QrCodeStoredResponse,
    summary="Update saved QR code",
    description=requires_capability("qr-generator", "write"),
    dependencies=[Depends(require_capability("qr-generator", "write"))],
)
async def update_saved_qr_code(
    qr_id: Annotated[int, Path(ge=1)],
    data: QrCodeUpdate,
    registry: DbRegistry,
    user: AuthorizedUser,
) -> QrCodeStoredResponse:
    svc = QrLibraryService(registry)
    return await svc.update_saved(
        qr_id,
        data,
        actor_id=user.id,
        is_superuser=user_has_permission(user, SUPERUSER_PERMISSION),
    )


@router.get(
    "/library/{qr_id}/svg",
    summary="Download saved QR SVG",
    response_class=Response,
    description=requires_capability("qr-generator", "read"),
    dependencies=[Depends(require_capability("qr-generator", "read"))],
)
async def get_saved_qr_svg(
    qr_id: Annotated[int, Path(ge=1)],
    registry: DbRegistry,
    user: AuthorizedUser,
) -> Response:
    svc = QrLibraryService(registry)
    svg = await svc.render_svg(
        qr_id,
        actor_id=user.id,
        is_superuser=user_has_permission(user, SUPERUSER_PERMISSION),
    )
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "private, max-age=300"},
    )
