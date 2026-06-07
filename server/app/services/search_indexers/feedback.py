from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.feedback import Feedback
from app.db.models.search_document import SearchVisibility
from app.services.search_index import (
    SearchDocumentInput,
    remove_by_source,
    upsert_document,
)
from app.services.search_source_types import SearchSourceType

FEEDBACK_SOURCE_TYPE = SearchSourceType.FEEDBACK


def _feedback_document(feedback: Feedback) -> SearchDocumentInput:
    return SearchDocumentInput(
        source_type=FEEDBACK_SOURCE_TYPE,
        source_id=feedback.id,
        title=f"Feedback: {feedback.theme}",
        body=f"Status: {feedback.status}\n{feedback.message}",
        url="/admin/tools/feedback",
        visibility=SearchVisibility.ADMIN,
    )


async def index_feedback(db: AsyncSession, feedback: Feedback) -> None:
    await upsert_document(db, _feedback_document(feedback))


async def remove_feedback(db: AsyncSession, feedback_id: int) -> None:
    await remove_by_source(db, FEEDBACK_SOURCE_TYPE, feedback_id)
