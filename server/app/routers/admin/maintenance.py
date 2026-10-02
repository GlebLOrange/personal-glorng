"""Superuser-only DB maintenance trigger with Turnstile gate."""

from fastapi import APIRouter, Depends, Request, status

from app.core.deps import AdminUser, AppSettings
from app.core.rate_limit import rate_limit_admin
from app.schemas.maintenance import (
    MaintenanceRunRequest,
    MaintenanceRunResponse,
    MaintenanceStatusResponse,
)
from app.services.maintenance import (
    get_maintenance_snapshot,
    start_maintenance,
    verify_turnstile_token,
)

router = APIRouter(dependencies=[Depends(rate_limit_admin)])


@router.get(
    "",
    response_model=MaintenanceStatusResponse,
    summary="Get DB maintenance status",
)
async def get_maintenance_status(
    _admin: AdminUser,
    settings: AppSettings,
) -> MaintenanceStatusResponse:
    status_value, detail = get_maintenance_snapshot()
    return MaintenanceStatusResponse(
        site_key=settings.TURNSTILE_SITE_KEY.strip(),
        enabled=settings.db_maintenance_ready(),
        status=status_value,
        detail=detail,
    )


@router.post(
    "/run",
    response_model=MaintenanceRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start DB maintenance",
)
async def run_maintenance(
    body: MaintenanceRunRequest,
    request: Request,
    _admin: AdminUser,
    settings: AppSettings,
) -> MaintenanceRunResponse:
    client_ip = request.client.host if request.client else None
    await verify_turnstile_token(
        settings,
        body.turnstile_token,
        remote_ip=client_ip,
    )
    status_value, detail = await start_maintenance(settings)
    return MaintenanceRunResponse(status=status_value, detail=detail)
