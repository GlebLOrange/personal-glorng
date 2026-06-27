"""Business logic for curated news articles."""

import html
import ipaddress
import json
import re
from html.parser import HTMLParser
from math import ceil
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.json_lists import parse_json_string_list
from app.core.logging import logger
from app.core.utils import paginate_params, utc_now
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
    NewsSourceUpdate,
)
from app.services.audit import AuditService
from app.services.search_indexers.news import index_news_article, remove_news_article

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_SLUG_RETRY_LIMIT = 5
_METADATA_MAX_BYTES = 200_000
_METADATA_TIMEOUT_SECONDS = 5.0


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


def _duplicate_key_field(exc: DuplicateKeyError) -> str | None:
    """Return the Mongo duplicate key field when the driver includes it."""
    key_pattern = (exc.details or {}).get("keyPattern") or {}
    if len(key_pattern) == 1:
        return next(iter(key_pattern))
    errmsg = str(exc)
    if "source_url" in errmsg:
        return "source_url"
    if "slug" in errmsg:
        return "slug"
    if "host" in errmsg:
        return "host"
    return None


class _TitleParser(HTMLParser):
    """Extract page title metadata from a small HTML document."""

    def __init__(self) -> None:
        """Initialize title collection state."""
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.meta_titles: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Capture title and common metadata tags."""
        if tag.lower() == "title":
            self.in_title = True
            return
        if tag.lower() != "meta":
            return
        attr_map = {key.lower(): value for key, value in attrs if value}
        name = (attr_map.get("property") or attr_map.get("name") or "").lower()
        if name in {"og:title", "twitter:title"} and attr_map.get("content"):
            self.meta_titles.append(attr_map["content"])

    def handle_endtag(self, tag: str) -> None:
        """Stop title capture after the closing title tag."""
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        """Append text inside the title tag."""
        if self.in_title:
            self.title_parts.append(data)

    def best_title(self) -> str | None:
        """Return the best extracted title."""
        title = _clean_metadata_text(" ".join(self.title_parts), max_length=90)
        if title:
            return title
        for value in self.meta_titles:
            title = _clean_metadata_text(value, max_length=90)
            if title:
                return title
        return None


def _is_public_feed_url(url: str) -> bool:
    """Return whether a feed URL is safe for server-side fetching."""
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    try:
        ip = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        return parsed.hostname not in {"localhost", "metadata.google.internal"}
    return not (ip.is_private or ip.is_loopback or ip.is_link_local)


def _require_public_feed_url(feed_url: str) -> None:
    """Reject feed URLs that could target local infrastructure."""
    if not _is_public_feed_url(feed_url):
        raise ValidationError("Feed URL must be a public http(s) URL")


def _canonical_url(value: str) -> str:
    """Normalize URL casing and remove fragments."""
    parts = urlsplit(value.strip())
    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path or "/",
            parts.query,
            "",
        )
    )


def _normalized_host(value: str) -> str:
    """Return a stable source host for a URL."""
    parsed = urlsplit(value)
    if not parsed.hostname:
        raise ValidationError("Article URL must include a host")
    host = parsed.hostname.rstrip(".").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def _homepage_url(value: str) -> str:
    """Return a source homepage URL from an article URL."""
    parts = urlsplit(value)
    host = parts.hostname or ""
    return urlunsplit((parts.scheme.lower(), host.lower(), "/", "", ""))


def _source_name_from_host(host: str) -> str:
    """Build a readable source name from a host."""
    labels = host.split(".")
    stem = labels[0] if labels else host
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", stem) if part) or host


def _clean_metadata_text(value: str | None, *, max_length: int) -> str:
    """Normalize fetched metadata text."""
    if not value:
        return ""
    return " ".join(html.unescape(value).split())[:max_length]


def _extract_title(document: str) -> str | None:
    """Extract title metadata from HTML."""
    parser = _TitleParser()
    parser.feed(document)
    return parser.best_title()


def _article_source_fields(
    data: NewsArticleCreate,
    source: NewsSource | None,
) -> dict[str, str | int | None]:
    """Return article source fields from a selected source or payload."""
    source_name = source.name if source else data.source_name
    source_feed_url = source.feed_url if source else (
        str(data.source_feed_url) if data.source_feed_url else None
    )
    if not source_name or not source_feed_url:
        raise ValidationError("News source is required")
    return {
        "source_id": source.id if source else data.source_id,
        "source_name": source_name,
        "source_feed_url": source_feed_url,
    }


def _article_payload_from_create(
    data: NewsArticleCreate,
    slug: str,
    source: NewsSource | None,
) -> dict[str, Any]:
    """Build a document payload from create data."""
    published_at = utc_now() if data.status == "published" else None
    source_fields = _article_source_fields(data, source)
    return {
        "slug": slug,
        "status": data.status,
        **source_fields,
        "source_url": str(data.source_url),
        "source_published_at": data.source_published_at,
        "original_title": data.original_title,
        "title": data.title,
        "summary": data.summary,
        "bullets": _dumps_json_list(data.bullets or []),
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
    source: NewsSource | None,
) -> NewsArticle:
    """Apply update payload to an article document."""
    updates = data.model_dump(exclude_unset=True)
    if source is not None:
        updates["source_id"] = source.id
        updates["source_name"] = source.name
        updates["source_feed_url"] = source.feed_url
    for field in ("bullets", "themes"):
        if field in updates and updates[field] is not None:
            updates[field] = _dumps_json_list(updates[field])
    for field in ("source_url", "source_feed_url"):
        if field in updates and updates[field] is not None:
            updates[field] = str(updates[field])
    if updates.get("slug"):
        updates["slug"] = _slugify(str(updates["slug"]))
    if updates.get("status") == "published" and article.published_at is None:
        updates["published_at"] = utc_now()
    merged = article.model_dump()
    merged.update(updates)
    return NewsArticle.model_validate(merged)


def _source_payload_from_create(data: NewsSourceCreate) -> dict[str, Any]:
    """Build a source document payload from create data."""
    feed_url = str(data.feed_url)
    _require_public_feed_url(feed_url)
    host = data.host or _normalized_host(feed_url)
    return {
        "name": data.name,
        "feed_url": feed_url,
        "host": host,
        "category": data.category,
        "region": data.region,
        "enabled": data.enabled,
    }


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
            themes=_loads_json_list("themes", article.themes),
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
        _require_public_feed_url(source_url)
        host = _normalized_host(source_url)
        existing = await self._sources().get_by_host(host)
        if existing is not None:
            return existing
        feed_url = source_feed_url or _homepage_url(source_url)
        existing = await self._sources().get_by_feed_url(feed_url)
        if existing is not None:
            if existing.host is None:
                return await self._sources().update_fields(existing.id, host=host)
            return existing
        data = NewsSourceCreate(
            name=source_name or _source_name_from_host(host),
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
        normalized_url = _canonical_url(source_url)
        _require_public_feed_url(normalized_url)
        try:
            async with (
                httpx.AsyncClient(
                    follow_redirects=True,
                    timeout=_METADATA_TIMEOUT_SECONDS,
                ) as client,
                client.stream(
                    "GET",
                    normalized_url,
                    headers={"Accept": "text/html,application/xhtml+xml"},
                ) as response,
            ):
                response.raise_for_status()
                final_url = _canonical_url(str(response.url))
                _require_public_feed_url(final_url)
                chunks: list[bytes] = []
                total = 0
                async for chunk in response.aiter_bytes():
                    total += len(chunk)
                    if total > _METADATA_MAX_BYTES:
                        remaining = _METADATA_MAX_BYTES - (total - len(chunk))
                        chunks.append(chunk[: max(0, remaining)])
                        break
                    chunks.append(chunk)
        except httpx.HTTPError as exc:
            raise ValidationError("Could not load article URL") from exc
        encoding = response.encoding or "utf-8"
        document = b"".join(chunks).decode(encoding, errors="replace")
        host = _normalized_host(final_url)
        source = await self._get_or_create_source_for_url(final_url, actor_id=actor_id)
        title = _extract_title(document) or _source_name_from_host(host)
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
                source_feed_url=str(data.source_feed_url) if data.source_feed_url else None,
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
                source_feed_url=str(data.source_feed_url) if data.source_feed_url else None,
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

    async def list_sources(self) -> list[NewsSource]:
        """List admin-managed RSS sources."""
        return await self._sources().list_sources()

    async def create_source(
        self,
        data: NewsSourceCreate,
        *,
        actor_id: int | None = None,
    ) -> NewsSource:
        """Create an RSS source."""
        feed_url = str(data.feed_url)
        if await self._sources().get_by_feed_url(feed_url):
            raise ConflictError("News feed URL already exists")
        host = data.host or _normalized_host(feed_url)
        if await self._sources().get_by_host(host):
            raise ConflictError("News source host already exists")
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
            _require_public_feed_url(feed_url)
            existing = await self._sources().get_by_feed_url(feed_url)
            if existing is not None and existing.id != source_id:
                raise ConflictError("News feed URL already exists")
            updates["feed_url"] = feed_url
            updates.setdefault("host", _normalized_host(feed_url))
        if updates.get("host") is not None:
            host = str(updates["host"])
            existing = await self._sources().get_by_host(host)
            if existing is not None and existing.id != source_id:
                raise ConflictError("News source host already exists")
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

    async def delete_source(
        self,
        source_id: int,
        *,
        actor_id: int | None = None,
    ) -> None:
        """Delete an RSS source."""
        await self._sources().get(source_id)
        if await self._news().count_by_source_id(source_id):
            raise ConflictError("News source is used by existing articles")
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

    async def list_articles(
        self,
        *,
        status: NewsStatus | None = "published",
        page: int = 1,
        per_page: int = 20,
    ) -> NewsArticleListResponse:
        """List articles with pagination."""
        offset, limit = paginate_params(page, per_page)
        items = await self._news().list_articles(
            status=status,
            offset=offset,
            limit=limit,
        )
        total = await self._news().count_articles(
            status=status,
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
