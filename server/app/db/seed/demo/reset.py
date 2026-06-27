"""Demo database reset helpers."""

from app.core.logging import logger
from app.db.registry import DatabaseRegistry
from app.db.seed.builders.demo import DEMO_READER_EMAIL, DEMO_WRITER_EMAIL
from app.services.user import get_user_by_email

DEMO_USER_EMAILS = (DEMO_READER_EMAIL, DEMO_WRITER_EMAIL)

_TASK_COLLECTIONS = (
    "reminders",
    "task_status_history",
    "google_sync_queue",
    "task_intakes",
    "tasks",
)


async def reset_tool_tables(registry: DatabaseRegistry) -> None:
    """Remove demo tool rows in dependency-safe order."""
    mongo = registry.require_mongo()
    for name in _TASK_COLLECTIONS:
        await mongo[name].delete_many({})

    if registry.urls is not None:
        await registry.urls._col().delete_many({})
    if registry.feedback is not None:
        await registry.feedback._col().delete_many({})
    if registry.expenses is not None:
        await registry.expenses.expenses._col().delete_many({})
    if registry.recipes is not None:
        await registry.recipes._col().delete_many({})
    if registry.news is not None:
        await registry.news._col().delete_many({})
    if registry.news_sources is not None:
        await registry.news_sources._col().delete_many({})

    if registry.users is not None:
        for email in DEMO_USER_EMAILS:
            user = await get_user_by_email(registry, email)
            if user is not None:
                await registry.users.delete(user.id)

    logger.info("Demo tool tables reset")
