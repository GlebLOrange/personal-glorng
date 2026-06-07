"""Per-source search index sync helpers and reindex registry."""

from collections.abc import Awaitable, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.feedback import Feedback
from app.db.models.recipe import Recipe
from app.db.models.task import Task
from app.db.models.tool_expense import ToolExpense
from app.db.models.url import ShortenedUrl
from app.services.search_index import remove_by_source, upsert_document
from app.services.search_indexers.expense import index_expense
from app.services.search_indexers.feedback import index_feedback
from app.services.search_indexers.recipe import RECIPE_SOURCE_TYPE, index_recipe
from app.services.search_indexers.resume import index_resume
from app.services.search_indexers.task import index_task
from app.services.search_indexers.url import index_url
from app.services.search_source_types import SearchSourceType

ReindexFn = Callable[[AsyncSession], Awaitable[int]]


async def _reindex_recipes(db: AsyncSession) -> int:
    recipes = (await db.execute(select(Recipe))).scalars().all()
    for recipe in recipes:
        await index_recipe(db, recipe)
    return len(recipes)


async def _reindex_tasks(db: AsyncSession) -> int:
    tasks = (await db.execute(select(Task))).scalars().all()
    for task in tasks:
        await index_task(db, task)
    return len(tasks)


async def _reindex_expenses(db: AsyncSession) -> int:
    expenses = (await db.execute(select(ToolExpense))).scalars().all()
    for expense in expenses:
        await index_expense(db, expense)
    return len(expenses)


async def _reindex_feedback(db: AsyncSession) -> int:
    entries = (await db.execute(select(Feedback))).scalars().all()
    for entry in entries:
        await index_feedback(db, entry)
    return len(entries)


async def _reindex_urls(db: AsyncSession) -> int:
    urls = (await db.execute(select(ShortenedUrl))).scalars().all()
    for url in urls:
        await index_url(db, url)
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
