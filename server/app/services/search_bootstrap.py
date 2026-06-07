"""Startup helpers for the unified search index."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.feature_flags import is_ai_search_enabled
from app.core.logging import logger
from app.services.search_indexers.resume import index_resume


async def bootstrap_resume_index(db: AsyncSession) -> None:
    """Upsert resume chunks on startup when AI search is enabled."""
    if not is_ai_search_enabled():
        return
    count = await index_resume(db)
    await db.commit()
    logger.info("Resume search index bootstrapped", context={"documents": count})
