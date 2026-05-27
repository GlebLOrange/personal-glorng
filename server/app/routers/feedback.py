import asyncio
from html import escape

from fastapi import APIRouter, Depends
from sqlalchemy import select, update

from app.core.deps import AdminUser, DbSession
from app.core.logging import logger
from app.core.rate_limit import RateLimiter
from app.core.telegram import notify_admin
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackStatusUpdate
from app.settings import get_settings

router = APIRouter(prefix="/feedback", tags=["feedback"])

rate_limit_feedback = RateLimiter(requests=5, window=300)


@router.post(
    "",
    response_model=FeedbackResponse,
    dependencies=[Depends(rate_limit_feedback)],
)
async def create_feedback(data: FeedbackCreate, db: DbSession) -> Feedback:
    """Public endpoint -- visitors can submit feedback."""
    entry = Feedback(email=data.email, theme=data.theme, message=data.message)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
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


@router.get("", response_model=list[FeedbackResponse])
async def list_feedback(db: DbSession, _user: AdminUser) -> list[Feedback]:
    """Admin endpoint -- list all feedback, newest first."""
    result = await db.execute(
        select(Feedback).order_by(Feedback.created_at.desc())
    )
    return list(result.scalars().all())


@router.patch("/{feedback_id}/status", response_model=FeedbackResponse)
async def update_feedback_status(
    feedback_id: int,
    data: FeedbackStatusUpdate,
    db: DbSession,
    _user: AdminUser,
) -> Feedback:
    """Admin endpoint -- mark feedback as read or archived."""
    await db.execute(
        update(Feedback)
        .where(Feedback.id == feedback_id)
        .values(status=data.status)
    )
    await db.commit()
    result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    entry = result.scalar_one()
    return entry
