import asyncio
from html import escape

from fastapi import APIRouter, Depends
from sqlalchemy import select, update

from app.core.deps import AuthorizedUser, DbSession, require_capability
from app.core.logging import logger
from app.core.rate_limit import RateLimiter
from app.core.telegram import notify_admin
from app.db.models.audit_event import AuditActorType, AuditCategory, AuditSource
from app.db.models.feedback import Feedback
from app.openapi import requires_capability
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackStatusUpdate
from app.services.audit import AuditRecord, AuditService
from app.services.search_indexers.feedback import index_feedback
from app.settings import get_settings

router = APIRouter(prefix="/feedback", tags=["feedback"])

rate_limit_feedback = RateLimiter(requests=5, window=300)


@router.post(
    "",
    response_model=FeedbackResponse,
    summary="Submit feedback",
    description="Public endpoint — visitors can submit feedback.",
    dependencies=[Depends(rate_limit_feedback)],
)
async def create_feedback(data: FeedbackCreate, db: DbSession) -> Feedback:
    entry = Feedback(email=data.email, theme=data.theme, message=data.message)
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    await index_feedback(db, entry)
    await db.commit()
    logger.info(
        "Feedback created",
        context={"id": entry.id, "email": data.email},
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
async def list_feedback(db: DbSession, _user: AuthorizedUser) -> list[Feedback]:
    result = await db.execute(select(Feedback).order_by(Feedback.created_at.desc()))
    return list(result.scalars().all())


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
    db: DbSession,
    user: AuthorizedUser,
) -> Feedback:
    await db.execute(
        update(Feedback).where(Feedback.id == feedback_id).values(status=data.status)
    )
    await db.flush()
    result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    entry = result.scalar_one()

    await AuditService(db).record(
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
