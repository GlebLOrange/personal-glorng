from app.db.documents.feedback import Feedback
from app.db.documents.search import SearchVisibility
from app.db.registry import DatabaseRegistry
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


async def index_feedback(registry: DatabaseRegistry, feedback: Feedback) -> None:
    await upsert_document(registry, _feedback_document(feedback))


async def remove_feedback(registry: DatabaseRegistry, feedback_id: int) -> None:
    await remove_by_source(registry, FEEDBACK_SOURCE_TYPE, feedback_id)
