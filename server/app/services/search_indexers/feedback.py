from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.feedback import Feedback
from app.db.models.search_document import SearchVisibility
from app.services.search_index import SearchDocumentInput, SearchIndexService

FEEDBACK_SOURCE_TYPE = "feedback"


async def index_feedback(db: AsyncSession, feedback: Feedback) -> None:
    document = SearchDocumentInput(
        source_type=FEEDBACK_SOURCE_TYPE,
        source_id=feedback.id,
        title=f"Feedback: {feedback.theme}",
        body=f"{feedback.email}\n{feedback.message}",
        url="/admin/tools/feedback",
        visibility=SearchVisibility.ADMIN,
    )
    await SearchIndexService(db).upsert(document)
