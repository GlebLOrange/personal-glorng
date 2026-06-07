"""Per-source search index sync helpers and reindex registry."""

from collections.abc import Awaitable, Callable

from app.db.registry import DatabaseRegistry
from app.services.search_index import remove_by_source, upsert_document
from app.services.search_indexers.expense import index_expense
from app.services.search_indexers.feedback import index_feedback
from app.services.search_indexers.recipe import RECIPE_SOURCE_TYPE, index_recipe
from app.services.search_indexers.resume import index_resume
from app.services.search_indexers.task import index_task
from app.services.search_indexers.url import index_url
from app.services.search_source_types import SearchSourceType

ReindexFn = Callable[[DatabaseRegistry], Awaitable[int]]


async def _reindex_recipes(registry: DatabaseRegistry) -> int:
    if registry.recipes is None:
        return 0
    recipes = await registry.recipes.list(limit=10_000)
    for recipe in recipes:
        await index_recipe(registry, recipe)
    return len(recipes)


async def _reindex_tasks(registry: DatabaseRegistry) -> int:
    if registry.tasks is None:
        return 0
    tasks = await registry.tasks.list(limit=10_000)
    for task in tasks:
        await index_task(registry, task)
    return len(tasks)


async def _reindex_expenses(registry: DatabaseRegistry) -> int:
    if registry.expenses is None:
        return 0
    expenses = await registry.expenses.expenses.list(limit=10_000)
    for expense in expenses:
        await index_expense(registry, expense)
    return len(expenses)


async def _reindex_feedback(registry: DatabaseRegistry) -> int:
    if registry.feedback is None:
        return 0
    entries = await registry.feedback.list(limit=10_000)
    for entry in entries:
        await index_feedback(registry, entry)
    return len(entries)


async def _reindex_urls(registry: DatabaseRegistry) -> int:
    if registry.urls is None:
        return 0
    urls = await registry.urls.list(limit=10_000)
    for url in urls:
        await index_url(registry, url)
    return len(urls)


SEARCH_REINDEXERS: tuple[tuple[str, ReindexFn], ...] = (
    ("resume", index_resume),
    (RECIPE_SOURCE_TYPE, _reindex_recipes),
    (SearchSourceType.TASK, _reindex_tasks),
    (SearchSourceType.EXPENSE, _reindex_expenses),
    (SearchSourceType.FEEDBACK, _reindex_feedback),
    (SearchSourceType.URL, _reindex_urls),
)

__all__ = [
    "SEARCH_REINDEXERS",
    "SearchSourceType",
    "remove_by_source",
    "upsert_document",
]
