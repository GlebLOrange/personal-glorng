from collections.abc import Sequence
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.base import document_to_dict, utc_now
from app.db.documents.news import NewsArticle, NewsSource
from app.db.repositories.base import MongoRepository


class NewsSourceRepository(MongoRepository[NewsSource]):
    """Repository for admin-managed RSS news sources."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "news_sources", NewsSource)

    async def list_enabled(self) -> list[NewsSource]:
        """Return enabled sources in display order."""
        return await self.list(enabled=True, limit=500, sort=[("name", 1)])

    async def get_by_feed_url(self, feed_url: str) -> NewsSource | None:
        """Return a source by exact feed URL."""
        data = await self._col().find_one({"feed_url": feed_url})
        if data is None:
            return None
        return self.model.model_validate({k: v for k, v in data.items() if k != "_id"})


class NewsArticleRepository(MongoRepository[NewsArticle]):
    """Repository for admin-curated news articles."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "news_articles", NewsArticle)

    def _list_query(
        self,
        *,
        enabled: bool | None = None,
        statuses: Sequence[str] | None = None,
        source: str | None = None,
        category: str | None = None,
        region: str | None = None,
    ) -> dict[str, Any]:
        """Build a MongoDB query for article list filters."""
        query: dict[str, Any] = {}
        if enabled is not None:
            query["enabled"] = enabled
        if statuses:
            status_values = list(dict.fromkeys(statuses))
            status_query: dict[str, Any] = {"status": {"$in": status_values}}
            if "published" in status_values:
                status_query = {
                    "$or": [status_query, {"status": {"$exists": False}}],
                }
            query.update(status_query)
        if source is not None:
            query["source"] = source
        if category is not None:
            query["category"] = category
        if region is not None:
            query["region"] = region
        return query

    async def list_articles(
        self,
        *,
        enabled: bool | None = None,
        statuses: Sequence[str] | None = None,
        source: str | None = None,
        category: str | None = None,
        region: str | None = None,
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "published_at",
        sort_order: str = "desc",
    ) -> list[NewsArticle]:
        """Return articles filtered, sorted, and paginated by MongoDB."""
        direction = 1 if sort_order == "asc" else -1
        cursor = self._col().find(
            self._list_query(
                enabled=enabled,
                statuses=statuses,
                source=source,
                category=category,
                region=region,
            ),
        )
        cursor = cursor.skip(offset).limit(limit).sort([(sort_by, direction), ("id", direction)])
        return [
            self.model.model_validate({k: v for k, v in data.items() if k != "_id"})
            async for data in cursor
        ]

    async def count_articles(
        self,
        *,
        enabled: bool | None = None,
        statuses: Sequence[str] | None = None,
        source: str | None = None,
        category: str | None = None,
        region: str | None = None,
    ) -> int:
        """Count articles matching list filters."""
        return await self._col().count_documents(
            self._list_query(
                enabled=enabled,
                statuses=statuses,
                source=source,
                category=category,
                region=region,
            ),
        )

    async def list_enabled_filter_values(self) -> tuple[list[str], list[str], list[str]]:
        """Return filter values for enabled public articles."""
        query = self._list_query(enabled=True, statuses=("published",))
        sources = await self._col().distinct("source", query)
        categories = await self._col().distinct("category", query)
        regions = await self._col().distinct("region", query)
        return (
            sorted(source for source in sources if isinstance(source, str) and source),
            sorted(category for category in categories if isinstance(category, str) and category),
            sorted(region for region in regions if isinstance(region, str) and region),
        )

    async def get_by_link(self, link: str) -> NewsArticle | None:
        """Return a curated article by exact link."""
        data = await self._col().find_one({"link": link})
        if data is None:
            return None
        return self.model.model_validate({k: v for k, v in data.items() if k != "_id"})

    async def upsert_feed_article(self, article: NewsArticle) -> NewsArticle:
        """Insert or refresh a parser-created article by link."""
        existing = await self.get_by_link(article.link)
        if existing is not None:
            if existing.origin != "feed":
                return existing
            return await self.update_fields(
                existing.id,
                title=article.title,
                source=article.source,
                origin=existing.origin or article.origin,
                category=article.category,
                region=article.region,
                summary=article.summary,
                published_at=article.published_at,
            )

        now = utc_now()
        if article.id == 0:
            article.id = await self.next_id()
        article.created_at = article.created_at or now
        article.updated_at = now
        await self._col().update_one(
            {"link": article.link},
            {"$setOnInsert": document_to_dict(article)},
            upsert=True,
        )
        return article

    async def get_by_title(self, title: str) -> NewsArticle | None:
        """Return a curated article by exact title."""
        data = await self._col().find_one({"title": title})
        if data is None:
            return None
        return self.model.model_validate({k: v for k, v in data.items() if k != "_id"})
