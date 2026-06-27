"""Repository helpers for curated news articles."""

import re
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.news import NewsArticle, NewsStatus
from app.db.repositories.base import MongoRepository, _parse_doc


class NewsRepository(MongoRepository[NewsArticle]):
    """Mongo repository for news article queries."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        """Initialize the news repository."""
        super().__init__(db, "news_articles", NewsArticle)

    async def get_by_slug(self, slug: str) -> NewsArticle | None:
        """Return an article by slug."""
        data = await self._col().find_one({"slug": slug})
        return _parse_doc(NewsArticle, data) if data else None

    async def get_by_source_url(self, source_url: str) -> NewsArticle | None:
        """Return an article by canonical source URL."""
        data = await self._col().find_one({"source_url": source_url})
        return _parse_doc(NewsArticle, data) if data else None

    async def source_url_exists(self, source_url: str) -> bool:
        """Return whether a source URL is already stored."""
        return await self._col().count_documents({"source_url": source_url}, limit=1) > 0

    async def list_articles(
        self,
        *,
        status: NewsStatus | None = None,
        theme: str | None = None,
        source: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[NewsArticle]:
        """List articles with optional public/admin filters."""
        query = self._query(status=status, theme=theme, source=source)
        cursor = (
            self._col()
            .find(query)
            .sort([("published_at", -1), ("created_at", -1)])
            .skip(offset)
            .limit(limit)
        )
        return [_parse_doc(NewsArticle, row) async for row in cursor]

    async def count_articles(
        self,
        *,
        status: NewsStatus | None = None,
        theme: str | None = None,
        source: str | None = None,
    ) -> int:
        """Count articles with optional filters."""
        return await self._col().count_documents(
            self._query(status=status, theme=theme, source=source)
        )

    async def list_themes(self, *, status: NewsStatus = "published") -> list[str]:
        """Return distinct stored theme JSON values for articles."""
        values = await self._col().distinct("themes", {"status": status})
        return [str(value) for value in values if value]

    @staticmethod
    def _query(
        *,
        status: NewsStatus | None,
        theme: str | None,
        source: str | None,
    ) -> dict[str, Any]:
        """Build a Mongo query for article lists."""
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        if theme:
            query["themes"] = {"$regex": f'"{re.escape(theme)}"'}
        if source:
            query["source_name"] = source
        return query
