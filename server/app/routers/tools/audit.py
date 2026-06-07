from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import AuthorizedUser, DbSession, require_capability
from app.core.utils import paginate_params
from app.schemas.audit import AuditEventListResponse, AuditEventResponse
from app.schemas.date_filters import AuditDateFilter, audit_date_filter
from app.services.audit import AuditService

router = APIRouter(
    prefix="/audit",
    dependencies=[Depends(require_capability("audit", "read"))],
)


@router.get(
    "",
    response_model=AuditEventListResponse,
    description="Filter by inclusive date range (date_from, date_to).",
)
async def list_audit_events(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
    filters: Annotated[AuditDateFilter, Depends(audit_date_filter)],
    page: int = 1,
    per_page: int = 50,
    category: str | None = None,
    action: str | None = None,
) -> AuditEventListResponse:
    offset, limit = paginate_params(page, per_page)
    svc = AuditService(db)
    items, total = await svc.list_events(
        category=category,
        action=action,
        date_from=filters.date_from,
        date_to=filters.date_to,
        offset=offset,
        limit=limit,
    )
    return AuditEventListResponse(
        items=[AuditEventResponse.model_validate(i) for i in items],
        total=total,
    )
