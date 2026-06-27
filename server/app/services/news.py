"""Business logic for curated news articles."""

import json
import re
from math import ceil
from typing import Any

from app.core.exceptions import ConflictError, NotFoundError
from app.core.json_lists import parse_json_string_list
from app.core.utils import paginate_params, utc_now
from app.db.documents.news import NewsArticle, NewsStatus
from app.db.registry import DatabaseRegistry
from app.schemas.news import (
    NewsArticleCreate,
    NewsArticleListResponse,
    NewsArticleResponse,
    NewsArticleUpdate,
)
from app.services.audit import AuditService
from app.services.search_indexers.news import index_news_article, remove_news_article

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _loads_json_list(field: str, raw: str) -> list[str]:
    """Load a persisted JSON string list."""
    return parse_json_string_list(raw, strict=True, field=field)


def _dumps_json_list(value: list[str]) -> str:
    """Dump a list for storage."""
    return json.dumps(value)


def _slugify(value: str) -> str:
    """Return a URL-safe slug."""
    slug = _SLUG_RE.sub("-", value.lower()).strip("-")
    return slug[:80].strip("-") or "news"


def _article_payload_from_create(data: NewsArticleCreate, slug: str) -> dict[str, Any]:
    """Build a document payload from create data."""
    published_at = utc_now() if data.status == "published" else None
    return {
        "slug": slug,
        "status": data.status,
        "source_name": data.source_name,
        "source_url": str(data.source_url),
        "source_feed_url": str(data.source_feed_url),
        "source_published_at": data.source_published_at,
        "original_title": data.original_title,
        "title": data.title,
        "summary": data.summary,
        "bullets": _dumps_json_list(data.bullets),
        "themes": _dumps_json_list([str(theme) for theme in data.themes]),
        "language": data.language,
        "published_at": published_at,
        "ai_model": data.ai_model,
        "ai_input_hash": data.ai_input_hash,
        "ingest_error": data.ingest_error,
    }


def _apply_article_updates(
    article: NewsArticle,
    data: NewsArticleUpdate,
) -> NewsArticle:
    """Apply update payload to an article document."""
    updates = data.model_dump(exclude_unset=True)
    for field in ("bullets", "themes"):
        if field in updates and updates[field] is not None:
            updates[field] = _dumps_json_list(updates[field])
    for field in ("source_url", "source_feed_url"):
        if field in updates and updates[field] is not None:
            updates[field] = str(updates[field])
    if updates.get("status") == "published" and article.published_at is None:
        updates["published_at"] = utc_now()
    merged = article.model_dump()
    merged.update(updates)
    return NewsArticle.model_validate(merged)


class NewsService:
    """Service for news article CRUD and public listing."""

    def __init__(self, registry: DatabaseRegistry, audit_svc: AuditService) -> None:
        """Initialize the news service."""
        self.registry = registry
        self._audit = audit_svc

    def _news(self):
        """Return the initialized news repository."""
        if self.registry.news is None:
            msg = "News repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.news

    @staticmethod
    def _to_response(article: NewsArticle) -> NewsArticleResponse:
        """Convert an article document to an API response."""
        return NewsArticleResponse(
            id=article.id,
            slug=article.slug,
            status=article.status,
            source_name=article.source_name,
            source_url=article.source_url,
            source_feed_url=article.source_feed_url,
            source_published_at=article.source_published_at,
            original_title=article.original_title,
            title=article.title,
            summary=article.summary,
            bullets=_loads_json_list("bullets", article.bullets),
            themes=_loads_json_list("themes", article.themes),
            language=article.language,
            published_at=article.published_at,
            telegram_message_id=article.telegram_message_id,
            ai_model=article.ai_model,
            ingest_error=article.ingest_error,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )

    async def unique_slug(self, title: str) -> str:
        """Generate a slug that is unique among news articles."""
        base = _slugify(title)
        slug = base
        suffix = 2
        while await self._news().get_by_slug(slug):
            slug = f"{base}-{suffix}"
            suffix += 1
        return slug

    async def require_article(self, article_id: int) -> NewsArticle:
        """Return an article by id or raise."""
        return await self._news().get(article_id)

    async def get_public_article(self, slug: str) -> NewsArticleResponse:
        """Return a published article by slug."""
        article = await self._news().get_by_slug(slug)
        if article is None or article.status != "published":
            raise NotFoundError("News article not found")
        return self._to_response(article)

    async def create_article(
        self,
        data: NewsArticleCreate,
        *,
        actor_id: int | None = None,
    ) -> NewsArticleResponse:
        """Create a news article."""
        source_url = str(data.source_url)
        if await self._news().source_url_exists(source_url):
            raise ConflictError("News source URL already exists")
        article = NewsArticle.model_validate(
            _article_payload_from_create(data, await self.unique_slug(data.title))
        )
        article = await self._news().insert(article)
        await index_news_article(self.registry, article)
        await self._audit.record_domain(
            action="news.created",
            resource_type="news",
            resource_id=article.id,
            actor_id=actor_id,
            metadata={"title": article.title, "source": article.source_name},
        )
        return self._to_response(article)

    async def update_article(
        self,
        article_id: int,
        data: NewsArticleUpdate,
        *,
        actor_id: int | None = None,
    ) -> NewsArticleResponse:
        """Update a news article."""
        article = await self.require_article(article_id)
        if data.source_url is not None:
            source_url = str(data.source_url)
            existing = await self._news().get_by_source_url(source_url)
            if existing is not None and existing.id != article_id:
                raise ConflictError("News source URL already exists")
        updated = _apply_article_updates(article, data)
        article = await self._news().replace(updated)
        await index_news_article(self.registry, article)
        await self._audit.record_domain(
            action="news.updated",
            resource_type="news",
            resource_id=article.id,
            actor_id=actor_id,
        )
        return self._to_response(article)

    async def delete_article(
        self,
        article_id: int,
        *,
        actor_id: int | None = None,
    ) -> None:
        """Delete a news article."""
        await self.require_article(article_id)
        await self._news().delete(article_id)
        await remove_news_article(self.registry, article_id)
        await self._audit.record_domain(
            action="news.deleted",
            resource_type="news",
            resource_id=article_id,
            actor_id=actor_id,
        )

    async def set_telegram_message_id(
        self,
        article_id: int,
        message_id: int,
    ) -> NewsArticleResponse:
        """Store a Telegram message id after successful publish."""
        article = await self._news().update_fields(
            article_id,
            telegram_message_id=message_id,
        )
        return self._to_response(article)

    async def list_articles(
        self,
        *,
        status: NewsStatus | None = "published",
        theme: str | None = None,
        source: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> NewsArticleListResponse:
        """List articles with pagination."""
        offset, limit = paginate_params(page, per_page)
        items = await self._news().list_articles(
            status=status,
            theme=theme,
            source=source,
            offset=offset,
            limit=limit,
        )
        total = await self._news().count_articles(
            status=status,
            theme=theme,
            source=source,
        )
        return NewsArticleListResponse(
            items=[self._to_response(item) for item in items],
            total=total,
            page=max(1, page),
            per_page=limit,
            pages=ceil(total / limit) if total else 0,
        )

    async def list_themes(self) -> list[str]:
        """Return all public themes."""
        themes: set[str] = set()
        for raw in await self._news().list_themes():
            themes.update(_loads_json_list("themes", raw))
        return sorted(themes)
