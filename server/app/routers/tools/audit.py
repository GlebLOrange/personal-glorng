from datetime import date

from fastapi import APIRouter, Depends

from app.core.deps import AuthorizedUser, DbSession, require_capability
from app.core.utils import paginate_params
from app.schemas.audit import AuditEventListResponse, AuditEventResponse
from app.services.audit import AuditService

router = APIRouter(
    prefix="/audit",
    dependencies=[Depends(require_capability("audit", "read"))],
)


@router.get("", response_model=AuditEventListResponse)
async def list_audit_events(
    db: DbSession,
    user: AuthorizedUser,  # noqa: ARG001
    page: int = 1,
    per_page: int = 50,
    category: str | None = None,
    action: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> AuditEventListResponse:
    offset, limit = paginate_params(page, per_page)
    svc = AuditService(db)
    items, total = await svc.list_events(
        category=category,
        action=action,
        date_from=date_from,
        date_to=date_to,
        offset=offset,
        limit=limit,
    )
    return AuditEventListResponse(
        items=[AuditEventResponse.model_validate(i) for i in items],
        total=total,
    )
