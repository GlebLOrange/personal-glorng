import asyncio
from html import escape

from fastapi import APIRouter, Depends

from app.core.deps import AuthorizedUser, require_capability
from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.rate_limit import RateLimiter
from app.core.telegram import notify_admin
from app.db.deps import DbRegistry
from app.db.documents.audit import AuditActorType, AuditCategory, AuditSource
from app.db.documents.feedback import Feedback
from app.openapi import requires_capability
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackStatusUpdate
from app.services.audit import AuditRecord, AuditService
from app.services.auth import _auth_log_email
from app.services.search_indexers.feedback import index_feedback
from app.settings import get_settings

router = APIRouter(prefix="/feedback", tags=["feedback"])

rate_limit_feedback = RateLimiter(requests=5, window=300, fail_open=False)


@router.post(
    "",
    response_model=FeedbackResponse,
    summary="Submit feedback",
    description="Public endpoint — visitors can submit feedback.",
    dependencies=[Depends(rate_limit_feedback)],
)
async def create_feedback(data: FeedbackCreate, registry: DbRegistry) -> Feedback:
    if registry.feedback is None:
        raise ApiError(503, "Feedback repository is not initialized")

    entry = Feedback(email=data.email, theme=data.theme, message=data.message)
    entry = await registry.feedback.insert(entry)
    await index_feedback(registry, entry)
    logger.info(
        "Feedback created",
        context={"id": entry.id, "email": _auth_log_email(str(data.email))},
    )

    truncated = data.message[:500] + ("..." if len(data.message) > 500 else "")
    base_url = get_settings().BASE_URL.rstrip("/")
    link = f"{base_url}/admin/tools/feedback"
    text = (
        f"<b>New feedback</b> from {escape(data.email)}\n"
        f"<b>Theme:</b> {escape(data.theme)}\n---\n"
        f"{escape(truncated)}\n\n"
        f'<a href="{link}">Open in admin</a>'
    )
    _bg = asyncio.create_task(notify_admin(text))  # noqa: RUF006

    return entry


@router.get(
    "",
    response_model=list[FeedbackResponse],
    summary="List feedback",
    description=requires_capability("feedback", "read"),
    dependencies=[Depends(require_capability("feedback", "read"))],
)
async def list_feedback(
    registry: DbRegistry,
    _user: AuthorizedUser,
) -> list[Feedback]:
    if registry.feedback is None:
        raise ApiError(503, "Feedback repository is not initialized")
    return await registry.feedback.list(limit=500, sort=[("created_at", -1)])


@router.patch(
    "/{feedback_id}/status",
    response_model=FeedbackResponse,
    summary="Update feedback status",
    description=requires_capability("feedback", "write"),
    dependencies=[Depends(require_capability("feedback", "write"))],
)
async def update_feedback_status(
    feedback_id: int,
    data: FeedbackStatusUpdate,
    registry: DbRegistry,
    user: AuthorizedUser,
) -> Feedback:
    if registry.feedback is None:
        raise ApiError(503, "Feedback repository is not initialized")

    entry = await registry.feedback.update_fields(feedback_id, status=data.status)
    await index_feedback(registry, entry)

    await AuditService(registry).record(
        AuditRecord(
            category=AuditCategory.DOMAIN,
            action="feedback.status_changed",
            actor_type=AuditActorType.USER,
            actor_id=user.id,
            source=AuditSource.WEB_ADMIN,
            resource_type="feedback",
            resource_id=feedback_id,
            metadata={"status": data.status},
        ),
    )
    return entry
