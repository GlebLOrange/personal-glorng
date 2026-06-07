"""Startup helpers for the unified search index."""

from app.core.feature_flags import is_ai_search_enabled
from app.core.logging import logger
from app.db.registry import DatabaseRegistry
from app.services.search_indexers.resume import index_resume


async def bootstrap_resume_index(registry: DatabaseRegistry) -> None:
    """Upsert resume chunks on startup when AI search is enabled."""
    if not is_ai_search_enabled():
        return
    count = await index_resume(registry)
    logger.info("Resume search index bootstrapped", context={"documents": count})
