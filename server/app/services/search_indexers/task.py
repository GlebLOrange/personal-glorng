from app.db.documents.search import SearchVisibility
from app.db.documents.task import Task
from app.db.registry import DatabaseRegistry
from app.services.search_index import (
    SearchDocumentInput,
    remove_by_source,
    upsert_document,
)
from app.services.search_source_types import SearchSourceType

TASK_SOURCE_TYPE = SearchSourceType.TASK


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


async def index_task(registry: DatabaseRegistry, task: Task) -> None:
    await upsert_document(registry, _task_document(task))


async def remove_task(registry: DatabaseRegistry, task_id: int) -> None:
    await remove_by_source(registry, TASK_SOURCE_TYPE, task_id)
