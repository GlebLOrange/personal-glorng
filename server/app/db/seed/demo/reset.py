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


async def reset_tool_tables(
    registry: DatabaseRegistry,
    tools: frozenset[str] | None = None,
) -> None:
    """Remove demo tool rows in dependency-safe order.

    When ``tools`` is None, wipe every tool table (full seed reset).
    When ``tools`` is set, wipe only those collections. Demo users are
    removed only on a full wipe. Expense categories are never deleted.
    """
    wipe_all = tools is None

    def wants(name: str) -> bool:
        return wipe_all or (tools is not None and name in tools)

    mongo = registry.require_mongo()
    if wants("tasks"):
        for name in _TASK_COLLECTIONS:
            await mongo[name].delete_many({})

    if wants("urls") and registry.urls is not None:
        await registry.urls._col().delete_many({})
    if wants("feedback") and registry.feedback is not None:
        await registry.feedback._col().delete_many({})
    if wants("expenses") and registry.expenses is not None:
        await registry.expenses.expenses._col().delete_many({})
    if (wants("recipes") or wants("multicooker")) and registry.recipes is not None:
        await registry.recipes._col().delete_many({})
    if wants("news"):
        if registry.news is not None:
            await registry.news._col().delete_many({})
        if registry.news_sources is not None:
            await registry.news_sources._col().delete_many({})

    if wipe_all and registry.users is not None:
        for email in DEMO_USER_EMAILS:
            user = await get_user_by_email(registry, email)
            if user is not None:
                await registry.users.delete(user.id)

    logger.info(
        "Demo tool tables reset",
        context={"tools": sorted(tools) if tools is not None else "all"},
    )
