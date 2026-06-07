from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import AuditServiceDep, AuthorizedUser, require_capability
from app.core.pagination import PaginationParams, audit_pagination_params
from app.schemas.audit import AuditEventListResponse, AuditEventResponse
from app.schemas.date_filters import AuditDateFilter, audit_date_filter

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(require_capability("audit", "read"))],
)


@router.get(
    "",
    response_model=AuditEventListResponse,
    description="Filter by inclusive date range (date_from, date_to).",
)
async def list_audit_events(
    svc: AuditServiceDep,
    user: AuthorizedUser,  # noqa: ARG001
    filters: Annotated[AuditDateFilter, Depends(audit_date_filter)],
    pagination: Annotated[PaginationParams, Depends(audit_pagination_params)],
    category: str | None = None,
    action: str | None = None,
) -> AuditEventListResponse:
    items, total = await svc.list_events(
        category=category,
        action=action,
        date_from=filters.date_from,
        date_to=filters.date_to,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return AuditEventListResponse(
        items=[AuditEventResponse.model_validate(i) for i in items],
        total=total,
    )
