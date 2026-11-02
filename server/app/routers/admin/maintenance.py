"""Superuser-only multi-job maintenance trigger with Turnstile gate."""

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
    summary="Get maintenance status",
)
async def get_maintenance_status(
    _admin: AdminUser,
    settings: AppSettings,
) -> MaintenanceStatusResponse:
    snap = get_maintenance_snapshot()
    return MaintenanceStatusResponse(
        site_key=settings.TURNSTILE_SITE_KEY.strip(),
        enabled=settings.turnstile_configured(),
        host_jobs_ready=settings.db_maintenance_ready(),
        status=snap.status,
        detail=snap.detail,
        job=snap.job,
        report=snap.report,
    )


@router.post(
    "/run",
    response_model=MaintenanceRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start a maintenance job",
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
    snap = await start_maintenance(settings, body.job)
    return MaintenanceRunResponse(
        status=snap.status,
        detail=snap.detail,
        job=snap.job,
        report=snap.report,
    )
