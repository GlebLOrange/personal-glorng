"""Business logic for curated news articles."""

import re
from datetime import date
from math import ceil

import httpx
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.logging import logger
from app.core.pagination import build_paginated
from app.core.url_safety import get_public_http_url
from app.core.utils import DEFAULT_PER_PAGE, paginate_params, utc_now
from app.db.documents.news import NewsArticle, NewsSource, NewsStatus
from app.db.registry import DatabaseRegistry
from app.db.repositories.news import NewsRepository, NewsSourceRepository
from app.schemas.news import (
    NewsArticleCreate,
    NewsArticleListResponse,
    NewsArticleMetadataResponse,
    NewsArticleResponse,
    NewsArticleUpdate,
    NewsSourceCreate,
    NewsSourceListResponse,
    NewsSourceResponse,
    NewsSourceUpdate,
    NewsStatsResponse,
)
from app.services.audit import AuditService
from app.services.news.html_meta import (
    _METADATA_MAX_BYTES,
    _METADATA_TIMEOUT_SECONDS,
    NewsHtmlMeta,
)
from app.services.news.payloads import (
    _SLUG_RETRY_LIMIT,
    _apply_article_updates,
    _article_payload_from_create,
    _duplicate_key_field,
    _loads_json_list,
    _slugify,
    _source_payload_from_create,
)
from app.services.search_indexers.news import index_news_article, remove_news_article


class NewsService:
    """Service for news article CRUD and public listing."""

    def __init__(self, registry: DatabaseRegistry, audit_svc: AuditService) -> None:
        """Initialize the news service."""
        self.registry = registry
        self._audit = audit_svc

    def _news(self) -> NewsRepository:
        """Return the initialized news repository."""
        if self.registry.news is None:
            msg = "News repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.news

    def _sources(self) -> NewsSourceRepository:
        """Return the initialized news source repository."""
        if self.registry.news_sources is None:
            msg = "News source repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.news_sources

    @staticmethod
    def _to_response(article: NewsArticle) -> NewsArticleResponse:
        """Convert an article document to an API response."""
        return NewsArticleResponse(
            id=article.id,
            slug=article.slug,
            status=article.status,
            source_id=article.source_id,
            source_name=article.source_name,
            source_url=article.source_url,
            source_feed_url=article.source_feed_url,
            source_published_at=article.source_published_at,
            original_title=article.original_title,
            title=article.title,
            summary=article.summary,
            bullets=_loads_json_list("bullets", article.bullets),
            tags=_loads_json_list("tags", article.tags),
            language=article.language,
            published_at=article.published_at,
            telegram_message_id=article.telegram_message_id,
            ai_model=article.ai_model,
            ai_input_hash=article.ai_input_hash,
            ingest_error=article.ingest_error,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )

    async def unique_slug(self, title: str) -> str:
        """Generate a slug that is unique among news articles."""
        base = _slugify(title)
        suffix = 2
        slug = base
        while await self._news().get_by_slug(slug):
            slug = f"{base}-{suffix}"
            suffix += 1
        return slug

    async def unique_slug_after_conflict(self, title: str, attempted_slug: str) -> str:
        """Generate a slug after Mongo rejects a stale uniqueness check."""
        base = _slugify(title)
        match = re.fullmatch(rf"{re.escape(base)}-(\d+)", attempted_slug)
        suffix = int(match.group(1)) + 1 if match else 2
        slug = f"{base}-{suffix}"
        while await self._news().get_by_slug(slug):
            suffix += 1
            slug = f"{base}-{suffix}"
        return slug

    async def require_article(self, article_id: int) -> NewsArticle:
        """Return an article by id or raise."""
        return await self._news().get(article_id)

    async def _resolve_article_source(self, source_id: int | None) -> NewsSource | None:
        """Return a selected source for article writes."""
        if source_id is None:
            return None
        return await self._sources().get(source_id)

    async def _get_or_create_source_for_url(
        self,
        source_url: str,
        *,
        source_name: str | None = None,
        source_feed_url: str | None = None,
        actor_id: int | None = None,
    ) -> NewsSource:
        """Return an existing source for the URL host or create one."""
        NewsHtmlMeta.require_public_feed_url(source_url)
        host = NewsHtmlMeta.normalized_host(source_url)
        existing = await self._sources().get_by_host(host)
        if existing is not None:
            return existing
        feed_url = source_feed_url or NewsHtmlMeta.homepage_url(source_url)
        existing = await self._sources().get_by_feed_url(feed_url)
        if existing is not None:
            if existing.host is None:
                return await self._sources().update_fields(existing.id, host=host)
            return existing
        data = NewsSourceCreate(
            name=source_name or NewsHtmlMeta.source_name_from_host(host),
            feed_url=feed_url,
            host=host,
            category="world",
            region="global",
            enabled=True,
        )
        return await self.create_source(data, actor_id=actor_id)

    async def load_article_metadata(
        self,
        source_url: str,
        *,
        actor_id: int | None = None,
    ) -> NewsArticleMetadataResponse:
        """Fetch article metadata and ensure a matching source exists."""
        normalized_url = NewsHtmlMeta.canonical_url(source_url)
        NewsHtmlMeta.require_public_feed_url(normalized_url)
        try:
            async with httpx.AsyncClient(timeout=_METADATA_TIMEOUT_SECONDS) as client:
                result = await get_public_http_url(
                    client,
                    normalized_url,
                    headers={"Accept": "text/html,application/xhtml+xml"},
                )
            response = result.response
            try:
                response.raise_for_status()
                final_url = NewsHtmlMeta.canonical_url(result.url)
                NewsHtmlMeta.require_public_feed_url(final_url)
                content = response.content[:_METADATA_MAX_BYTES]
                encoding = response.encoding or "utf-8"
            finally:
                await response.aclose()
        except (httpx.HTTPError, ValueError) as exc:
            raise ValidationError("Could not load article URL") from exc
        document = content.decode(encoding, errors="replace")
        host = NewsHtmlMeta.normalized_host(final_url)
        source = await self._get_or_create_source_for_url(final_url, actor_id=actor_id)
        title = NewsHtmlMeta.extract_title(
            document
        ) or NewsHtmlMeta.source_name_from_host(host)
        return NewsArticleMetadataResponse(
            source_url=final_url,
            title=title,
            source_host=host,
            source_id=source.id,
            source_name=source.name,
            source_feed_url=source.feed_url,
        )

    async def get_public_article(self, slug: str) -> NewsArticleResponse:
        """Return a published article by slug."""
        article = await self._news().get_by_slug(slug)
        if article is None or article.status != "published":
            raise NotFoundError("News article not found")
        return self._to_response(article)

    async def get_article(self, article_id: int) -> NewsArticleResponse:
        """Return any article by id for admin tools."""
        article = await self.require_article(article_id)
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
        source = await self._resolve_article_source(data.source_id)
        if source is None:
            source = await self._get_or_create_source_for_url(
                source_url,
                source_name=data.source_name,
                source_feed_url=str(data.source_feed_url)
                if data.source_feed_url
                else None,
                actor_id=actor_id,
            )
        slug = await self.unique_slug(data.title)
        for _ in range(_SLUG_RETRY_LIMIT):
            article = NewsArticle.model_validate(
                _article_payload_from_create(data, slug, source)
            )
            try:
                article = await self._news().insert(article)
                break
            except DuplicateKeyError as exc:
                field = _duplicate_key_field(exc)
                if field == "source_url":
                    raise ConflictError("News source URL already exists") from exc
                if field != "slug":
                    raise
                slug = await self.unique_slug_after_conflict(data.title, slug)
        else:
            raise ConflictError("Could not generate a unique news URL")
        if article.status == "published":
            try:
                await index_news_article(self.registry, article)
            except Exception as exc:
                logger.warning(
                    "News article search indexing failed after create",
                    error=exc,
                    context={"article_id": article.id, "slug": article.slug},
                )
        await self._audit.record_domain(
            action="news.created",
            resource_type="news",
            resource_id=article.id,
            actor_id=actor_id,
            metadata={
                "title": article.title,
                "source": article.source_name,
                "source_id": article.source_id,
            },
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
        if data.slug is not None:
            existing = await self._news().get_by_slug(_slugify(data.slug))
            if existing is not None and existing.id != article_id:
                raise ConflictError("News slug already exists")
        if data.source_url is not None:
            source_url = str(data.source_url)
            existing = await self._news().get_by_source_url(source_url)
            if existing is not None and existing.id != article_id:
                raise ConflictError("News source URL already exists")
        source = await self._resolve_article_source(data.source_id)
        if source is None and data.source_url is not None:
            source = await self._get_or_create_source_for_url(
                str(data.source_url),
                source_name=data.source_name,
                source_feed_url=str(data.source_feed_url)
                if data.source_feed_url
                else None,
                actor_id=actor_id,
            )
        updated = _apply_article_updates(article, data, source)
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

    async def list_sources(
        self,
        *,
        enabled: bool | None = None,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> NewsSourceListResponse:
        """List admin-managed RSS sources with pagination."""
        offset, limit = paginate_params(page, per_page)
        sources = await self._sources().list_sources(
            enabled=enabled,
            offset=offset,
            limit=limit,
        )
        total = await self._sources().count_sources(enabled=enabled)
        items = [NewsSourceResponse.model_validate(source) for source in sources]
        safe_page = max(1, page)
        return build_paginated(
            items,
            total=total,
            page=safe_page,
            per_page=limit,
            response_cls=NewsSourceListResponse,
        )

    async def list_all_sources(self) -> list[NewsSource]:
        """List all RSS sources (internal use)."""
        return await self._sources().list_all_sources()

    async def create_source(
        self,
        data: NewsSourceCreate,
        *,
        actor_id: int | None = None,
    ) -> NewsSource:
        """Create an RSS source."""
        feed_url = str(data.feed_url)
        if await self._sources().get_by_feed_url(feed_url):
            raise ConflictError("A news source with this feed URL already exists")
        host = data.host or NewsHtmlMeta.normalized_host(feed_url)
        if await self._sources().get_by_host(host):
            raise ConflictError("A news source for this host already exists")
        source = await self._sources().insert(
            NewsSource.model_validate(_source_payload_from_create(data))
        )
        await self._audit.record_domain(
            action="news_source.created",
            resource_type="news_source",
            resource_id=source.id,
            actor_id=actor_id,
            metadata={"name": source.name},
        )
        return source

    async def update_source(
        self,
        source_id: int,
        data: NewsSourceUpdate,
        *,
        actor_id: int | None = None,
    ) -> NewsSource:
        """Update an RSS source."""
        source = await self._sources().get(source_id)
        updates = data.model_dump(exclude_unset=True)
        if data.feed_url is not None:
            feed_url = str(data.feed_url)
            NewsHtmlMeta.require_public_feed_url(feed_url)
            existing = await self._sources().get_by_feed_url(feed_url)
            if existing is not None and existing.id != source_id:
                raise ConflictError("A news source with this feed URL already exists")
            updates["feed_url"] = feed_url
            updates.setdefault("host", NewsHtmlMeta.normalized_host(feed_url))
        if updates.get("host") is not None:
            host = str(updates["host"])
            existing = await self._sources().get_by_host(host)
            if existing is not None and existing.id != source_id:
                raise ConflictError("A news source for this host already exists")
        merged = source.model_dump()
        merged.update(updates)
        updated = await self._sources().replace(NewsSource.model_validate(merged))
        await self._audit.record_domain(
            action="news_source.updated",
            resource_type="news_source",
            resource_id=source_id,
            actor_id=actor_id,
        )
        return updated

    async def record_source_fetch(
        self,
        source_id: int,
        *,
        last_error: str | None = None,
        etag: str | None = None,
        last_modified: str | None = None,
        clear_error: bool = False,
    ) -> NewsSource:
        """Persist last-fetch metadata after an ingest attempt."""
        fields: dict[str, object] = {"last_fetched_at": utc_now()}
        if clear_error:
            fields["last_error"] = None
        elif last_error is not None:
            fields["last_error"] = last_error[:500]
        if etag is not None:
            fields["etag"] = etag
        if last_modified is not None:
            fields["last_modified"] = last_modified
        return await self._sources().update_fields(source_id, **fields)

    async def delete_source(
        self,
        source_id: int,
        *,
        actor_id: int | None = None,
    ) -> None:
        """Delete an RSS source; detach article FKs, keep denormalized source text."""
        await self._sources().get(source_id)
        await self._news().clear_source_id(source_id)
        await self._sources().delete(source_id)
        await self._audit.record_domain(
            action="news_source.deleted",
            resource_type="news_source",
            resource_id=source_id,
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

    async def draft_demo_articles(self) -> int:
        """Move seeded demo articles to draft so the public list stays real."""
        return await self._news().draft_demo_articles()

    async def list_articles(
        self,
        *,
        status: NewsStatus | None = "published",
        tag: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> NewsArticleListResponse:
        """List articles with pagination and optional public filters."""
        offset, limit = paginate_params(page, per_page)
        items = await self._news().list_articles(
            status=status,
            tag=tag,
            date_from=date_from,
            date_to=date_to,
            offset=offset,
            limit=limit,
        )
        total = await self._news().count_articles(
            status=status,
            tag=tag,
            date_from=date_from,
            date_to=date_to,
        )
        return NewsArticleListResponse(
            items=[self._to_response(item) for item in items],
            total=total,
            page=max(1, page),
            per_page=limit,
            pages=ceil(total / limit) if total else 0,
        )

    async def list_tags(self) -> list[str]:
        """Return all public tags."""
        tags: set[str] = set()
        for raw in await self._news().list_tags():
            tags.update(_loads_json_list("tags", raw))
        return sorted(tags)

    async def news_stats(self) -> NewsStatsResponse:
        """Return article counts grouped by status for admin dashboards."""
        counts, total = await self._news().count_articles_by_status()
        return NewsStatsResponse(
            total=total,
            draft=counts.get("draft", 0),
            pending_review=counts.get("pending_review", 0),
            scheduled=counts.get("scheduled", 0),
            published=counts.get("published", 0),
            private=counts.get("private", 0),
            trash=counts.get("trash", 0),
        )
