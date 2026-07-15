"""Feedback listing service."""

from app.core.pagination import build_paginated
from app.core.utils import DEFAULT_PER_PAGE, paginate_params
from app.db.registry import DatabaseRegistry
from app.schemas.feedback import FeedbackListResponse, FeedbackResponse


async def list_feedback(
    registry: DatabaseRegistry,
    *,
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
    status: str | None = None,
) -> FeedbackListResponse:
    """List feedback entries with optional status filter."""
    if registry.feedback is None:
        msg = "Feedback repository is not initialized"
        raise RuntimeError(msg)

    offset, limit = paginate_params(page, per_page)
    filters: dict[str, str] = {}
    if status:
        filters["status"] = status
    items = await registry.feedback.list(
        offset=offset,
        limit=limit,
        sort=[("created_at", -1)],
        **filters,
    )
    total = await registry.feedback.count(**filters)
    responses = [FeedbackResponse.model_validate(item) for item in items]
    safe_page = max(1, page)
    return build_paginated(
        responses,
        total=total,
        page=safe_page,
        per_page=limit,
    )
