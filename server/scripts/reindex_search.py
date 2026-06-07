"""Backfill the search_documents index from all supported sources."""

import asyncio
import sys

from sqlalchemy import select

from app.db.models.feedback import Feedback
from app.db.models.recipe import Recipe
from app.db.models.task import Task
from app.db.models.tool_expense import ToolExpense
from app.db.models.url import ShortenedUrl
from app.db.session import get_session_factory
from app.services.search_indexers.expense import index_expense
from app.services.search_indexers.feedback import index_feedback
from app.services.search_indexers.recipe import index_recipe
from app.services.search_indexers.resume import index_resume
from app.services.search_indexers.task import index_task
from app.services.search_indexers.url import index_url


async def reindex_search() -> None:
    """Rebuild search documents from resume and database tables."""
    factory = get_session_factory()
    async with factory() as db:
        resume_count = await index_resume(db)

        recipes = (await db.execute(select(Recipe))).scalars().all()
        for recipe in recipes:
            await index_recipe(db, recipe)

        tasks = (await db.execute(select(Task))).scalars().all()
        for task in tasks:
            await index_task(db, task)

        expenses = (await db.execute(select(ToolExpense))).scalars().all()
        for expense in expenses:
            await index_expense(db, expense)

        feedback_entries = (await db.execute(select(Feedback))).scalars().all()
        for entry in feedback_entries:
            await index_feedback(db, entry)

        urls = (await db.execute(select(ShortenedUrl))).scalars().all()
        for url in urls:
            await index_url(db, url)

        await db.commit()
        print(  # noqa: T201
            "Search reindex complete:",
            f"resume={resume_count}",
            f"recipes={len(recipes)}",
            f"tasks={len(tasks)}",
            f"expenses={len(expenses)}",
            f"feedback={len(feedback_entries)}",
            f"urls={len(urls)}",
        )


def main() -> None:
    asyncio.run(reindex_search())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("reindex_search failed", file=sys.stderr)  # noqa: T201
        raise
