from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import AuthorizedUser, require_capability
from app.core.pagination import (
    PaginationParams,
    audit_pagination_params,
    build_paginated,
)
from app.db.deps import DbRegistry
from app.schemas.app_log import AppLogListResponse, AppLogResponse
from app.schemas.date_filters import AuditDateFilter, audit_date_filter
from app.services.app_log import AppLogService

router = APIRouter(
    prefix="/app-logs",
    tags=["app-logs"],
    dependencies=[Depends(require_capability("app-logs", "read"))],
)


def get_app_log_service(registry: DbRegistry) -> AppLogService:
    return AppLogService(registry)


AppLogServiceDep = Annotated[AppLogService, Depends(get_app_log_service)]


@router.get(
    "",
    response_model=AppLogListResponse,
    description="Filter by level, request_id, message substring, and date range.",
)
async def list_app_logs(
    svc: AppLogServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    filters: Annotated[AuditDateFilter, Depends(audit_date_filter)],
    pagination: Annotated[PaginationParams, Depends(audit_pagination_params)],
    level: Annotated[str | None, Query(pattern=r"^(debug|info|warning|error)$")] = None,
    request_id: str | None = None,
    message: str | None = None,
) -> AppLogListResponse:
    items, total = await svc.list_logs(
        level=level,
        request_id=request_id,
        message=message,
        date_from=filters.date_from,
        date_to=filters.date_to,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return build_paginated(
        [AppLogResponse.model_validate(item) for item in items],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )
