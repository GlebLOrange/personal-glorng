from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.search_document import SearchVisibility
from app.db.models.task import Task
from app.services.search_index import SearchDocumentInput, SearchIndexService

TASK_SOURCE_TYPE = "task"


def _task_document(task: Task) -> SearchDocumentInput:
    body_parts = [task.title]
    if task.description:
        body_parts.append(task.description)
    if task.location:
        body_parts.append(f"Location: {task.location}")
    body_parts.append(f"Status: {task.status.value}")

    return SearchDocumentInput(
        source_type=TASK_SOURCE_TYPE,
        source_id=task.id,
        title=task.title,
        body="\n".join(body_parts),
        url="/admin/tools/tasks",
        visibility=SearchVisibility.ADMIN,
    )


async def index_task(db: AsyncSession, task: Task) -> None:
    await SearchIndexService(db).upsert(_task_document(task))


async def remove_task(db: AsyncSession, task_id: int) -> None:
    await SearchIndexService(db).delete_by_source(TASK_SOURCE_TYPE, task_id)
