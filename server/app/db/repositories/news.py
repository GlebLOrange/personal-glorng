"""Repository helpers for curated news articles."""

import json
import re
from datetime import UTC, date, datetime, time

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.utils import DEFAULT_PER_PAGE
from app.db.documents.base import utc_now
from app.db.documents.news import NewsArticle, NewsSource, NewsStatus
from app.db.repositories.base import MongoRepository, _parse_doc


def _news_tag_pattern(tag: str) -> str:
    """Match a complete tag inside the JSON-string tags field."""
    return re.escape(json.dumps(tag))


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
        tag: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[NewsArticle]:
        """List articles with optional status, tag, and date filters."""
        query = self._query(
            status=status,
            tag=tag,
            date_from=date_from,
            date_to=date_to,
        )
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
        tag: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        """Count articles with optional status, tag, and date filters."""
        return await self._col().count_documents(
            self._query(
                status=status,
                source_id=source_id,
                tag=tag,
                date_from=date_from,
                date_to=date_to,
            )
        )

    async def draft_demo_articles(self) -> int:
        """Move seeded demo articles off the public published list."""
        result = await self._col().update_many(
            {"ai_model": "demo", "status": "published"},
            {"$set": {"status": "draft", "updated_at": utc_now()}},
        )
        return int(result.modified_count)

    async def count_articles_by_status(self) -> tuple[dict[str, int], int]:
        """Count articles by status in one aggregation; total includes missing status."""
        cursor = self._col().aggregate(
            [{"$group": {"_id": "$status", "count": {"$sum": 1}}}],
        )
        counts: dict[str, int] = {}
        total = 0
        async for row in cursor:
            count = int(row["count"])
            total += count
            status = row.get("_id")
            if status is None:
                continue
            counts[str(status)] = count
        return counts, total

    async def clear_source_id(self, source_id: int) -> int:
        """Detach articles from a deleted source; keep denormalized source fields."""
        result = await self._col().update_many(
            {"source_id": source_id},
            {"$set": {"source_id": None, "updated_at": utc_now()}},
        )
        return int(result.modified_count)

    async def list_tags(self, *, status: NewsStatus = "published") -> list[str]:
        """Return distinct stored tag JSON values for articles."""
        values = await self._col().distinct("tags", {"status": status})
        return [str(value) for value in values if value]

    @staticmethod
    def _query(
        *,
        status: NewsStatus | None,
        source_id: int | None = None,
        tag: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict[str, object]:
        """Build a Mongo query for article lists."""
        query: dict[str, object] = {}
        if status:
            query["status"] = status
        if source_id is not None:
            query["source_id"] = source_id
        if tag:
            query["tags"] = {"$regex": _news_tag_pattern(tag)}
        if date_from is not None or date_to is not None:
            bounds: dict[str, datetime] = {}
            if date_from is not None:
                bounds["$gte"] = datetime.combine(date_from, time.min, tzinfo=UTC)
            if date_to is not None:
                bounds["$lte"] = datetime.combine(date_to, time.max, tzinfo=UTC)
            query["source_published_at"] = bounds
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
