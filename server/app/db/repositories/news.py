"""Repository helpers for curated news articles."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.utils import DEFAULT_PER_PAGE
from app.db.documents.news import NewsArticle, NewsSource, NewsStatus
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
        return (
            await self._col().count_documents({"source_url": source_url}, limit=1) > 0
        )

    async def list_articles(
        self,
        *,
        status: NewsStatus | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[NewsArticle]:
        """List articles with optional status filter."""
        query = self._query(status=status)
        cursor = (
            self._col()
            .find(query)
            .sort(
                [
                    ("source_published_at", -1),
                    ("published_at", -1),
                    ("created_at", -1),
                ]
            )
            .skip(offset)
            .limit(limit)
        )
        return [_parse_doc(NewsArticle, row) async for row in cursor]

    async def count_articles(
        self,
        *,
        status: NewsStatus | None = None,
        source_id: int | None = None,
    ) -> int:
        """Count articles with optional status filter."""
        return await self._col().count_documents(
            self._query(status=status, source_id=source_id)
        )

    async def count_by_source_id(self, source_id: int) -> int:
        """Count articles that reference a source."""
        return await self.count_articles(source_id=source_id)

    async def list_themes(self, *, status: NewsStatus = "published") -> list[str]:
        """Return distinct stored theme JSON values for articles."""
        values = await self._col().distinct("themes", {"status": status})
        return [str(value) for value in values if value]

    @staticmethod
    def _query(
        *,
        status: NewsStatus | None,
        source_id: int | None = None,
    ) -> dict[str, NewsStatus | int]:
        """Build a Mongo query for article lists."""
        query: dict[str, NewsStatus | int] = {}
        if status:
            query["status"] = status
        if source_id is not None:
            query["source_id"] = source_id
        return query


class NewsSourceRepository(MongoRepository[NewsSource]):
    """Mongo repository for RSS/Atom source queries."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        """Initialize the news source repository."""
        super().__init__(db, "news_sources", NewsSource)

    async def get_by_feed_url(self, feed_url: str) -> NewsSource | None:
        """Return a source by feed URL."""
        data = await self._col().find_one({"feed_url": feed_url})
        return _parse_doc(NewsSource, data) if data else None

    async def get_by_host(self, host: str) -> NewsSource | None:
        """Return a source by normalized host."""
        data = await self._col().find_one({"host": host})
        return _parse_doc(NewsSource, data) if data else None

    async def list_sources(
        self,
        *,
        enabled: bool | None = None,
        offset: int = 0,
        limit: int = DEFAULT_PER_PAGE,
    ) -> list[NewsSource]:
        """List sources ordered for admin display."""
        query: dict[str, bool] = {}
        if enabled is not None:
            query["enabled"] = enabled
        cursor = (
            self._col()
            .find(query)
            .sort([("name", 1), ("id", 1)])
            .skip(offset)
            .limit(limit)
        )
        return [_parse_doc(NewsSource, row) async for row in cursor]

    async def count_sources(self, *, enabled: bool | None = None) -> int:
        """Count news sources with optional enabled filter."""
        query: dict[str, bool] = {}
        if enabled is not None:
            query["enabled"] = enabled
        return await self._col().count_documents(query)

    async def list_all_sources(self) -> list[NewsSource]:
        """List all sources ordered for admin display."""
        cursor = self._col().find({}).sort([("name", 1), ("id", 1)])
        return [_parse_doc(NewsSource, row) async for row in cursor]
