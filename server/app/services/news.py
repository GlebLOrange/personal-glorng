"""RSS news source management and public feed aggregation."""

import asyncio
import calendar
import ipaddress
import re
import socket
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from html import unescape
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlparse

import feedparser
import httpx
from pydantic import ValidationError as PydanticValidationError
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import ApiError, ConflictError, ValidationError
from app.core.logging import logger
from app.db.deps import DbRegistry
from app.db.documents.news import NewsArticle, NewsSource
from app.db.repositories.news import NewsArticleRepository
from app.schemas.news import (
    NewsArticleResponse,
    NewsArticleSortField,
    NewsArticleStatus,
    NewsListResponse,
    SortOrder,
    news_source_key,
    sanitize_news_article_link,
    sanitize_news_source_url,
    source_from_news_article_link,
    source_from_news_source_url,
    source_home_url_from_news_article_link,
    title_from_news_article_link,
)
from app.schemas.validators import validate_clean_optional

DEFAULT_NEWS_PER_PAGE = 20
MAX_PUBLIC_FEED_SOURCES = 8
FEED_TIMEOUT_SECONDS = 2.5
FEED_REFRESH_BUDGET_SECONDS = 3.0
ARTICLE_METADATA_MAX_BYTES = 256_000
ARTICLE_METADATA_MAX_REDIRECTS = 3
_TAG_RE = re.compile(r"<[^>]+>")
DW_ATOM_FEED_URL = "https://rss.dw.com/atom/rss-en-top"
DW_LEGACY_FEED_URL = "https://rss.dw.com/rdf/rss-en-top"

DEFAULT_NEWS_SOURCES: tuple[dict[str, str], ...] = (
    {
        "name": "BBC News",
        "feed_url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "world",
        "region": "global",
    },
    {
        "name": "Reuters",
        "feed_url": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
        "category": "world",
        "region": "global",
    },
    {
        "name": "The Guardian",
        "feed_url": "https://www.theguardian.com/world/rss",
        "category": "world",
        "region": "global",
    },
    {
        "name": "Al Jazeera",
        "feed_url": "https://www.aljazeera.com/xml/rss/all.xml",
        "category": "world",
        "region": "global",
    },
    {
        "name": "NPR",
        "feed_url": "https://feeds.npr.org/1004/rss.xml",
        "category": "world",
        "region": "north america",
    },
    {
        "name": "DW",
        "feed_url": DW_ATOM_FEED_URL,
        "category": "world",
        "region": "europe",
    },
    {
        "name": "France 24",
        "feed_url": "https://www.france24.com/en/rss",
        "category": "world",
        "region": "europe",
    },
    {
        "name": "CBC",
        "feed_url": "https://www.cbc.ca/cmlink/rss-world",
        "category": "world",
        "region": "north america",
    },
    {
        "name": "The Japan Times",
        "feed_url": "https://www.japantimes.co.jp/feed/",
        "category": "world",
        "region": "asia",
    },
    {
        "name": "ABC Australia",
        "feed_url": "https://www.abc.net.au/news/feed/51120/rss.xml",
        "category": "world",
        "region": "oceania",
    },
)

FeedParser = Callable[[bytes, NewsSource], list[NewsArticle]]
MetadataFetcher = Callable[[str], Awaitable[dict[str, str]]]
CacheInvalidator = Callable[[], Awaitable[None]]


def _repo(registry: DbRegistry):
    if registry.news_sources is None:
        raise ApiError(503, "News source repository is not initialized")
    return registry.news_sources


def _article_repo(registry: DbRegistry):
    if registry.news_articles is None:
        raise ApiError(503, "News article repository is not initialized")
    return registry.news_articles


def _is_public_ip(address: str) -> bool:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return False
    return ip.is_global


async def validate_public_feed_url(url: str, *, label: str = "Feed URL") -> str:
    """Reject non-public URLs before the server fetches an admin-provided URL."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValidationError(f"{label} must be an http(s) URL")
    if parsed.username or parsed.password:
        raise ValidationError(f"{label} must not include credentials")

    host = parsed.hostname.strip().lower()
    if host == "localhost" or host.endswith(".localhost"):
        raise ValidationError(f"{label} host is not allowed")
    try:
        direct_ip = ipaddress.ip_address(host)
    except ValueError:
        direct_ip = None
    if direct_ip is not None and not direct_ip.is_global:
        raise ValidationError(f"{label} host is not public")

    try:
        infos = await asyncio.to_thread(
            socket.getaddrinfo,
            host,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except OSError as exc:
        raise ValidationError(f"{label} host could not be resolved") from exc

    addresses = {info[4][0] for info in infos}
    if not addresses or any(not _is_public_ip(address) for address in addresses):
        raise ValidationError(f"{label} must resolve to public addresses")
    return url


async def ensure_default_news_sources(registry: DbRegistry) -> None:
    """Seed editable starter sources when the collection is empty."""
    repo = _repo(registry)
    if await repo.count() > 0:
        legacy_dw = await repo.get_by_feed_url(DW_LEGACY_FEED_URL)
        atom_dw = await repo.get_by_feed_url(DW_ATOM_FEED_URL)
        if legacy_dw is not None and atom_dw is None:
            await repo.update_fields(legacy_dw.id, feed_url=DW_ATOM_FEED_URL)
        return
    for item in DEFAULT_NEWS_SOURCES:
        try:
            await repo.insert(NewsSource(**item))
        except DuplicateKeyError:
            continue


async def create_news_source(registry: DbRegistry, data: dict[str, Any]) -> NewsSource:
    """Create or return a validated RSS source."""
    repo = _repo(registry)
    raw_feed_url = str(data["feed_url"])
    feed_url = await validate_public_feed_url(sanitize_news_source_url(raw_feed_url))
    existing = await repo.get_by_feed_url(feed_url)
    if existing is not None:
        return existing
    payload = dict(data)
    payload["feed_url"] = feed_url
    if not str(payload.get("name") or "").strip():
        payload["name"] = source_from_news_source_url(raw_feed_url) or ""
    return await repo.insert(NewsSource(**payload))


async def update_news_source(
    registry: DbRegistry,
    source_id: int,
    data: dict[str, Any],
) -> NewsSource:
    """Update a validated RSS source."""
    repo = _repo(registry)
    if "feed_url" in data:
        data["feed_url"] = await validate_public_feed_url(
            sanitize_news_source_url(str(data["feed_url"])),
        )
        existing = await repo.get_by_feed_url(data["feed_url"])
        if existing is not None and existing.id != source_id:
            raise ConflictError("A source with this feed URL already exists")
    return await repo.update_fields(source_id, **data)


async def invalidate_public_news_cache() -> None:
    """Placeholder for public news cache invalidation."""


class _ArticleMetadataParser(HTMLParser):
    """Extract basic article metadata from an HTML document."""

    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.meta: dict[str, str] = {}
        self._is_title = False

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Capture title and meta tag values."""
        if tag.lower() == "title":
            self._is_title = True
            return
        if tag.lower() != "meta":
            return
        attr_map = {key.lower(): value for key, value in attrs if value}
        key = attr_map.get("property") or attr_map.get("name")
        content = attr_map.get("content")
        if key and content:
            self.meta[key.lower()] = content

    def handle_endtag(self, tag: str) -> None:
        """Stop collecting title text at the closing title tag."""
        if tag.lower() == "title":
            self._is_title = False

    def handle_data(self, data: str) -> None:
        """Collect text inside the title tag."""
        if self._is_title:
            self.title_parts.append(data)

    def metadata(self) -> dict[str, str]:
        """Return normalized article metadata fields."""
        title = (
            self.meta.get("og:title")
            or self.meta.get("twitter:title")
            or " ".join(self.title_parts)
        )
        description = (
            self.meta.get("og:description")
            or self.meta.get("twitter:description")
            or self.meta.get("description")
        )
        site_name = self.meta.get("og:site_name") or self.meta.get("application-name")
        values = {
            "title": _clean_text(title, max_length=180),
            "summary": _clean_text(description, max_length=500),
            "source": _clean_text(site_name, max_length=120),
        }
        return {key: value for key, value in values.items() if value}


async def fetch_article_metadata(link: str) -> dict[str, str]:
    """Fetch a public article URL and extract basic HTML metadata."""
    current_url = await validate_public_feed_url(link, label="Article URL")
    timeout = httpx.Timeout(
        FEED_TIMEOUT_SECONDS,
        connect=1.0,
        read=FEED_TIMEOUT_SECONDS,
        write=1.0,
        pool=1.0,
    )
    async with httpx.AsyncClient(timeout=timeout) as client:
        for _ in range(ARTICLE_METADATA_MAX_REDIRECTS + 1):
            async with client.stream("GET", current_url, follow_redirects=False) as response:
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        return {}
                    current_url = await validate_public_feed_url(
                        urljoin(str(response.url), location),
                        label="Article URL",
                    )
                    continue

                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if content_type and "html" not in content_type:
                    return {}
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) >= ARTICLE_METADATA_MAX_BYTES:
                        break
                parser = _ArticleMetadataParser()
                parser.feed(bytes(content).decode(response.encoding or "utf-8", errors="replace"))
                return parser.metadata()
    return {}


async def _apply_article_metadata_defaults(
    payload: dict[str, Any],
    metadata_fetcher: MetadataFetcher,
) -> None:
    """Fill blank manual article fields from its linked page when available."""
    link = str(payload.get("link") or "").strip()
    if not link:
        return
    should_fetch = (
        not str(payload.get("title") or "").strip()
        or not str(payload.get("summary") or "").strip()
        or str(payload.get("source") or "").strip() in {"", "gLOrng"}
    )
    if not should_fetch:
        return
    try:
        metadata = await metadata_fetcher(link)
    except (httpx.HTTPError, OSError, TypeError, UnicodeError, ValidationError, ValueError) as exc:
        logger.warning(
            "News article metadata fetch failed",
            context={"link": link, "error": str(exc)[:300]},
        )
        return

    if not str(payload.get("title") or "").strip() and metadata.get("title"):
        payload["title"] = metadata["title"]
    if not str(payload.get("summary") or "").strip() and metadata.get("summary"):
        payload["summary"] = metadata["summary"]
    source = str(payload.get("source") or "").strip()
    if source in {"", "gLOrng"} and metadata.get("source"):
        payload["source"] = metadata["source"]


async def _prepare_article_payload(
    data: dict[str, Any],
    metadata_fetcher: MetadataFetcher,
) -> dict[str, Any]:
    """Normalize manual article payload fields before persistence."""
    payload = dict(data)
    payload.pop("source_feed_url", None)
    raw_link = str(payload.get("link") or "")
    if not raw_link:
        return payload

    payload["link"] = sanitize_news_article_link(raw_link)
    await _apply_article_metadata_defaults(payload, metadata_fetcher)
    if not str(payload.get("title") or "").strip():
        payload["title"] = title_from_news_article_link(raw_link) or ""
    source = str(payload.get("source") or "").strip()
    if not source or source == "gLOrng":
        payload["source"] = source_from_news_article_link(raw_link) or source or "gLOrng"
    return payload


async def _resolve_article_source(registry: DbRegistry, payload: dict[str, Any]) -> None:
    """Use or create the editable source object that matches an article URL."""
    link = str(payload.get("link") or "")
    if not link:
        return

    await ensure_default_news_sources(registry)
    repo = _repo(registry)
    sources = await repo.list(limit=500, sort=[("name", 1)])
    sources_by_key = {news_source_key(source.name): source for source in sources}

    selected_source = str(payload.get("source") or "").strip()
    if selected_source and selected_source != "gLOrng":
        existing = sources_by_key.get(news_source_key(selected_source))
        if existing is not None:
            payload["source"] = existing.name
            return

    source_name = source_from_news_article_link(link)
    if source_name is None:
        return

    existing = sources_by_key.get(news_source_key(source_name))
    if existing is not None:
        payload["source"] = existing.name
        return

    feed_url = source_home_url_from_news_article_link(link) or link
    try:
        source = await repo.insert(
            NewsSource(
                name=source_name,
                feed_url=feed_url,
                category=str(payload.get("category") or "world"),
                region=str(payload.get("region") or "global"),
                enabled=False,
            ),
        )
    except DuplicateKeyError:
        source = await repo.get_by_feed_url(feed_url)
        if source is None:
            raise
    payload["source"] = source.name


async def create_news_article(
    registry: DbRegistry,
    data: dict[str, Any],
    *,
    metadata_fetcher: MetadataFetcher = fetch_article_metadata,
    cache_invalidator: CacheInvalidator = invalidate_public_news_cache,
) -> NewsArticle:
    """Create or update an admin-curated news article by link."""
    repo = _article_repo(registry)
    payload = await _prepare_article_payload(data, metadata_fetcher)
    await _resolve_article_source(registry, payload)
    existing = await repo.get_by_link(payload["link"])
    if existing is not None:
        article = await repo.update_fields(existing.id, **payload)
        await cache_invalidator()
        return article
    try:
        article = await repo.insert(NewsArticle(**payload))
    except DuplicateKeyError as exc:
        existing = await repo.get_by_link(payload["link"])
        if existing is not None:
            article = await repo.update_fields(existing.id, **payload)
        else:
            raise ConflictError(_news_article_conflict_message(exc)) from exc
    await cache_invalidator()
    return article


async def update_news_article(
    registry: DbRegistry,
    article_id: int,
    data: dict[str, Any],
    *,
    metadata_fetcher: MetadataFetcher = fetch_article_metadata,
    cache_invalidator: CacheInvalidator = invalidate_public_news_cache,
) -> NewsArticle:
    """Update an admin-curated news article."""
    repo = _article_repo(registry)
    payload = await _prepare_article_payload(data, metadata_fetcher)
    await _resolve_article_source(registry, payload)
    await _ensure_unique_news_article_link(
        repo,
        link=payload.get("link"),
        article_id=article_id,
    )
    try:
        article = await repo.update_fields(article_id, **payload)
    except DuplicateKeyError as exc:
        raise ConflictError(_news_article_conflict_message(exc)) from exc
    await cache_invalidator()
    return article


async def _ensure_unique_news_article_link(
    repo: NewsArticleRepository,
    *,
    link: str | None,
    article_id: int | None = None,
) -> None:
    """Reject duplicate curated article links."""
    if link:
        existing = await repo.get_by_link(link)
        if existing is not None and existing.id != article_id:
            raise ConflictError("A news article with this link already exists")


def _duplicate_key_fields(exc: DuplicateKeyError) -> set[str]:
    """Return MongoDB duplicate-key field names when PyMongo exposes them."""
    details = getattr(exc, "details", None)
    if not isinstance(details, dict):
        return set()
    fields: set[str] = set()
    for key in ("keyPattern", "keyValue"):
        value = details.get(key)
        if isinstance(value, dict):
            fields.update(str(field) for field in value)
    return fields


def _news_article_conflict_message(exc: DuplicateKeyError) -> str:
    """Return a precise admin-facing duplicate article message."""
    fields = _duplicate_key_fields(exc)
    if "link" in fields:
        return "A news article with this link already exists"
    if "title" in fields:
        return "A news article with this title already exists"
    return "A news article conflicts with an existing record"


def _clean_text(value: str | None, *, max_length: int = 500) -> str | None:
    if not value:
        return None
    cleaned = unescape(_TAG_RE.sub(" ", value))
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        return None
    return cleaned[:max_length]


def _entry_datetime(entry: object) -> datetime | None:
    parsed = getattr(entry, "published_parsed", None) or getattr(
        entry,
        "updated_parsed",
        None,
    )
    if parsed is None:
        return None
    return datetime.fromtimestamp(calendar.timegm(parsed), tz=UTC)


def _entry_link(entry: object, source: NewsSource) -> str | None:
    raw_link = str(getattr(entry, "link", "")).strip()
    if not raw_link:
        return None
    link = urljoin(source.feed_url, raw_link)
    parsed = urlparse(link)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return link


def _entry_summary(entry: object) -> str | None:
    """Extract the best available plain-text summary from RSS or Atom entries."""
    for attr in ("summary", "description"):
        summary = _clean_text(str(getattr(entry, attr, "") or ""))
        if summary:
            return summary

    content = getattr(entry, "content", None)
    if not isinstance(content, list) or not content:
        return None
    first = content[0]
    value = first.get("value") if isinstance(first, dict) else getattr(first, "value", None)
    return _clean_text(str(value or ""))


def normalize_feed_articles(content: bytes, source: NewsSource) -> list[NewsArticle]:
    """Parse RSS/Atom bytes into stored article documents."""
    parsed = feedparser.parse(content)
    articles: list[NewsArticle] = []
    for entry in parsed.entries:
        title = _clean_text(str(getattr(entry, "title", "")), max_length=180)
        link = _entry_link(entry, source)
        if not title or not link:
            continue
        articles.append(
            NewsArticle(
                title=title,
                link=link,
                source=source.name,
                origin="feed",
                status="published",
                category=source.category,
                region=source.region,
                summary=_entry_summary(entry),
                published_at=_entry_datetime(entry) or datetime.now(UTC),
            ),
        )
    return articles


def _manual_article_response(article: NewsArticle) -> NewsArticleResponse:
    """Convert a stored article to the public article shape."""
    return NewsArticleResponse(
        id=f"{article.origin}-{article.id}",
        title=article.title,
        link=article.link,
        source=article.source,
        category=article.category,
        region=article.region,
        summary=article.summary,
        published_at=article.published_at,
        status=article.status or "published",
        created_at=article.created_at,
        updated_at=article.updated_at,
        editable=article.origin == "manual",
    )


async def _fetch_public_url_bytes(
    client: httpx.AsyncClient,
    url: str,
    *,
    label: str,
) -> bytes:
    """Fetch a public URL while validating every redirect target."""
    current_url = await validate_public_feed_url(url, label=label)
    for _ in range(ARTICLE_METADATA_MAX_REDIRECTS + 1):
        response = await client.get(current_url, follow_redirects=False)
        if response.is_redirect:
            location = response.headers.get("location")
            if not location:
                raise ValidationError(f"{label} redirect is missing a location")
            current_url = await validate_public_feed_url(
                urljoin(str(response.url), location),
                label=label,
            )
            continue
        response.raise_for_status()
        return response.content
    raise ValidationError(f"{label} exceeded the redirect limit")


async def _fetch_source(
    client: httpx.AsyncClient,
    registry: DbRegistry,
    source: NewsSource,
    parser: FeedParser,
) -> int:
    repo = _repo(registry)
    article_repo = _article_repo(registry)
    try:
        content = await _fetch_public_url_bytes(client, source.feed_url, label="Feed URL")
        articles = await asyncio.to_thread(parser, content, source)
        for article in articles:
            await article_repo.upsert_feed_article(article)
    except (
        httpx.HTTPError,
        AttributeError,
        PydanticValidationError,
        TypeError,
        ValidationError,
        ValueError,
    ) as exc:
        error = str(exc)[:300]
        logger.warning(
            "News feed fetch failed",
            context={"source_id": source.id, "source": source.name, "error": error},
        )
        await repo.update_fields(source.id, last_error=error)
        return 0

    await repo.update_fields(
        source.id,
        last_error=None,
        last_fetched_at=datetime.now(UTC),
    )
    return len(articles)


async def _fetch_sources(
    client: httpx.AsyncClient,
    registry: DbRegistry,
    sources: list[NewsSource],
    parser: FeedParser,
) -> tuple[int, bool]:
    """Fetch enabled feeds into MongoDB within a small request budget."""
    tasks = [
        asyncio.create_task(_fetch_source(client, registry, source, parser))
        for source in sources[:MAX_PUBLIC_FEED_SOURCES]
    ]
    if not tasks:
        return 0, False

    done, pending = await asyncio.wait(tasks, timeout=FEED_REFRESH_BUDGET_SECONDS)
    for task in pending:
        task.cancel()
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)
        logger.warning(
            "News feed refresh budget exceeded",
            context={
                "pending_sources": len(pending),
                "budget_seconds": FEED_REFRESH_BUDGET_SECONDS,
            },
        )

    stored_count = 0
    for task in done:
        try:
            stored_count += task.result()
        except Exception as exc:
            logger.warning("News feed task failed", error=exc)
    return stored_count, bool(pending)


async def refresh_news_from_sources(
    registry: DbRegistry,
    *,
    source_ids: list[int] | None = None,
    parser: FeedParser = normalize_feed_articles,
    cache_invalidator: CacheInvalidator = invalidate_public_news_cache,
) -> int:
    """Parse enabled RSS feeds and persist their articles."""
    await ensure_default_news_sources(registry)
    sources = await _repo(registry).list_enabled()
    if source_ids:
        selected_ids = set(source_ids)
        sources = [source for source in sources if source.id in selected_ids]
    timeout = httpx.Timeout(
        FEED_TIMEOUT_SECONDS,
        connect=1.0,
        read=FEED_TIMEOUT_SECONDS,
        write=1.0,
        pool=1.0,
    )
    async with httpx.AsyncClient(timeout=timeout) as client:
        stored_count, _has_partial_feed = await _fetch_sources(client, registry, sources, parser)
    await cache_invalidator()
    return stored_count


def _clean_public_filter(value: str | None, *, max_length: int) -> str | None:
    """Normalize optional public text filters before querying MongoDB."""
    return validate_clean_optional(value, max_length=max_length)


async def get_public_news(
    registry: DbRegistry,
    *,
    page: int = 1,
    per_page: int = DEFAULT_NEWS_PER_PAGE,
    source: str | None = None,
    category: str | None = None,
    region: str | None = None,
    statuses: list[NewsArticleStatus] | None = None,  # noqa: ARG001
    sort_by: NewsArticleSortField = "published_at",
    sort_order: SortOrder = "desc",
) -> NewsListResponse:
    """Load public news articles from MongoDB."""
    repo = _article_repo(registry)
    start = (page - 1) * per_page
    effective_statuses: list[NewsArticleStatus] = ["published"]
    source = _clean_public_filter(source, max_length=120)
    category = _clean_public_filter(category, max_length=64)
    region = _clean_public_filter(region, max_length=64)
    articles = [
        _manual_article_response(article)
        for article in await repo.list_articles(
            enabled=True,
            statuses=effective_statuses,
            source=source,
            category=category,
            region=region,
            offset=start,
            limit=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ]
    total = await repo.count_articles(
        enabled=True,
        statuses=effective_statuses,
        source=source,
        category=category,
        region=region,
    )
    sources, categories, regions = await repo.list_enabled_filter_values()
    response = NewsListResponse(
        articles=articles,
        sources=sources,
        categories=categories,
        regions=regions,
        page=page,
        per_page=per_page,
        total=total,
        pages=(total + per_page - 1) // per_page,
        updated_at=datetime.now(UTC),
    )
    return response


class NewsService:
    """News business operations with small injectable parser/fetch/cache seams."""

    def __init__(
        self,
        registry: DbRegistry,
        *,
        parser: FeedParser = normalize_feed_articles,
        metadata_fetcher: MetadataFetcher = fetch_article_metadata,
        cache_invalidator: CacheInvalidator = invalidate_public_news_cache,
    ) -> None:
        self.registry = registry
        self.parser = parser
        self.metadata_fetcher = metadata_fetcher
        self.cache_invalidator = cache_invalidator

    async def ensure_default_sources(self) -> None:
        """Seed default news sources when needed."""
        await ensure_default_news_sources(self.registry)

    async def list_sources(self) -> list[NewsSource]:
        """List admin-managed RSS sources."""
        await self.ensure_default_sources()
        return await _repo(self.registry).list(limit=500, sort=[("name", 1)])

    async def create_source(self, data: dict[str, Any]) -> NewsSource:
        """Create an RSS source and invalidate public news cache."""
        source = await create_news_source(self.registry, data)
        await self.cache_invalidator()
        return source

    async def update_source(self, source_id: int, data: dict[str, Any]) -> NewsSource:
        """Update an RSS source and invalidate public news cache."""
        source = await update_news_source(self.registry, source_id, data)
        await self.cache_invalidator()
        return source

    async def delete_source(self, source_id: int) -> None:
        """Delete an RSS source and invalidate public news cache."""
        await _repo(self.registry).delete(source_id)
        await self.cache_invalidator()

    async def refresh_from_sources(self, *, source_ids: list[int] | None = None) -> int:
        """Parse enabled RSS sources using the configured parser."""
        return await refresh_news_from_sources(
            self.registry,
            source_ids=source_ids,
            parser=self.parser,
            cache_invalidator=self.cache_invalidator,
        )

    async def get_public_news(
        self,
        *,
        page: int = 1,
        per_page: int = DEFAULT_NEWS_PER_PAGE,
        source: str | None = None,
        category: str | None = None,
        region: str | None = None,
        sort_by: NewsArticleSortField = "published_at",
        sort_order: SortOrder = "desc",
    ) -> NewsListResponse:
        """Load public published news articles."""
        return await get_public_news(
            self.registry,
            page=page,
            per_page=per_page,
            source=source,
            category=category,
            region=region,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def list_admin_articles(
        self,
        *,
        statuses: list[NewsArticleStatus] | None = None,
        sort_by: NewsArticleSortField = "published_at",
        sort_order: SortOrder = "desc",
    ) -> list[NewsArticle]:
        """List admin-visible news articles."""
        return await _article_repo(self.registry).list_articles(
            statuses=statuses,
            limit=500,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def create_article(self, data: dict[str, Any]) -> NewsArticle:
        """Create or update a curated article by link."""
        return await create_news_article(
            self.registry,
            data,
            metadata_fetcher=self.metadata_fetcher,
            cache_invalidator=self.cache_invalidator,
        )

    async def update_article(self, article_id: int, data: dict[str, Any]) -> NewsArticle:
        """Update a curated article."""
        return await update_news_article(
            self.registry,
            article_id,
            data,
            metadata_fetcher=self.metadata_fetcher,
            cache_invalidator=self.cache_invalidator,
        )

    async def delete_article(self, article_id: int) -> None:
        """Delete a curated article and invalidate public news cache."""
        await _article_repo(self.registry).delete(article_id)
        await self.cache_invalidator()
