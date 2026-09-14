"""Trusted RSS/Atom ingestion for curated news."""

import asyncio
import hashlib
import html
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from xml.etree.ElementTree import Element, ParseError

import httpx
from defusedxml.common import DefusedXmlException

from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.url_safety import get_public_http_url, is_public_http_url
from app.core.xml_security import has_unsafe_xml_declaration, parse_xml
from app.db.documents.news import NewsSource
from app.schemas.news import (
    ALLOWED_NEWS_TAGS,
    NewsArticleCreate,
    NewsIngestResponse,
)
from app.services.llm_json import complete_json, groq_api_key
from app.services.news import NewsService
from app.settings import get_settings

_TAG_RE = re.compile(r"<[^>]+>")
_XML_ENCODING_RE = re.compile(
    rb"<\?xml[^>]*encoding=['\"]([^'\"]+)['\"]",
    re.IGNORECASE,
)
_MAX_FEED_BYTES = 1_000_000
_TRACKING_QUERY_KEYS = frozenset(
    {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "fbclid",
        "gclid",
        "mc_cid",
        "mc_eid",
    }
)
_FEED_HEADERS = {
    "User-Agent": (
        "GlebY-NewsBot/1.0 (+https://gleblorange.github.io/personal-glorng/; news-ingest)"
    ),
    "Accept": (
        "application/rss+xml, application/atom+xml, application/xml, "
        "text/xml;q=0.9, */*;q=0.1"
    ),
}
_SYSTEM_PROMPT = """You write concise curated news summaries.
Use only facts present in the supplied feed metadata.
Return JSON with: title, summary, bullets, tags, telegram_text.
Do not invent details. Keep attribution neutral and do not copy publisher prose."""


@dataclass(frozen=True)
class NewsSourceConfig:
    """Trusted source configuration."""

    name: str
    feed_url: str
    id: int | None = None
    enabled: bool = True
    default_themes: tuple[str, ...] = ("world",)
    max_items_per_run: int = 5
    language: str = "en"
    etag: str | None = None
    last_modified: str | None = None


@dataclass(frozen=True)
class FeedItem:
    """Normalized feed item."""

    title: str
    url: str
    excerpt: str
    published_at: datetime | None


def _clean_text(value: str | None, *, max_length: int = 2_000) -> str:
    """Strip HTML tags and normalize whitespace."""
    if not value:
        return ""
    text = html.unescape(_TAG_RE.sub(" ", value))
    return " ".join(text.split())[:max_length]


def _local_name(tag: str) -> str:
    """Return an XML element's local name without namespace URI."""
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _canonical_url(value: str, *, base_url: str) -> str:
    """Normalize a feed item URL for dedupe (drop fragment and tracking params)."""
    joined = urljoin(base_url, value.strip())
    parts = urlsplit(joined)
    query = urlencode(
        [
            (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
            if key.lower() not in _TRACKING_QUERY_KEYS
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path, query, ""))


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse common RSS/Atom datetime values."""
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except TypeError, ValueError:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _find_child(parent: Element, *local_names: str) -> Element | None:
    """Return the first direct child whose local name matches."""
    wanted = set(local_names)
    for child in parent:
        if _local_name(child.tag) in wanted:
            return child
    return None


def _child_text(parent: Element, *local_names: str) -> str | None:
    """Return trimmed text from the first matching direct child."""
    node = _find_child(parent, *local_names)
    if node is None or node.text is None:
        return None
    text = node.text.strip()
    return text or None


def _item_link(item: Element) -> str:
    """Resolve an item URL from link, atom:link href, or permalink guid."""
    text_link = ""
    alternate_href = ""
    any_href = ""
    for child in item:
        if _local_name(child.tag) != "link":
            continue
        text = (child.text or "").strip()
        if text and not text_link:
            text_link = text
        href = child.attrib.get("href", "").strip()
        if not href:
            continue
        rel = child.attrib.get("rel", "alternate")
        if rel == "alternate" and not alternate_href:
            alternate_href = href
        elif not any_href:
            any_href = href
    if text_link:
        return text_link
    if alternate_href:
        return alternate_href
    if any_href:
        return any_href
    guid = _find_child(item, "guid", "id")
    if guid is not None:
        is_permalink = guid.attrib.get("isPermaLink", "true").lower()
        text = (guid.text or "").strip()
        if text and is_permalink != "false":
            return text
    return ""


def _item_excerpt(item: Element) -> str:
    """Pick the best available excerpt/summary field."""
    for name in ("description", "encoded", "summary", "content"):
        text = _child_text(item, name)
        if text:
            return _clean_text(text)
    return ""


def _item_published(item: Element) -> datetime | None:
    """Parse pubDate / dc:date / Atom published|updated."""
    for name in ("pubDate", "published", "updated", "date"):
        text = _child_text(item, name)
        if text:
            parsed = _parse_datetime(text)
            if parsed is not None:
                return parsed
    return None


def _source_from_raw(raw: dict[str, Any]) -> NewsSourceConfig:
    """Parse one source config object."""
    name = _clean_text(str(raw.get("name", "")), max_length=120)
    feed_url = str(raw.get("feed_url", "")).strip()
    if not name or not feed_url or not is_public_http_url(feed_url):
        msg = "Invalid news source config"
        raise ValueError(msg)
    themes = tuple(
        theme
        for theme in raw.get("default_themes", ["world"])
        if isinstance(theme, str) and theme in ALLOWED_NEWS_TAGS
    )
    etag = raw.get("etag")
    last_modified = raw.get("last_modified")
    return NewsSourceConfig(
        name=name,
        feed_url=feed_url,
        id=raw.get("id") if isinstance(raw.get("id"), int) else None,
        enabled=bool(raw.get("enabled", True)),
        default_themes=themes or ("world",),
        max_items_per_run=max(1, min(int(raw.get("max_items_per_run", 5)), 20)),
        language=_clean_text(str(raw.get("language", "en")), max_length=12) or "en",
        etag=etag if isinstance(etag, str) and etag.strip() else None,
        last_modified=(
            last_modified
            if isinstance(last_modified, str) and last_modified.strip()
            else None
        ),
    )


def load_news_sources() -> list[NewsSourceConfig]:
    """Load trusted news sources from settings."""
    raw = get_settings().NEWS_SOURCES_JSON.strip()
    if not raw:
        return []
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        msg = "NEWS_SOURCES_JSON must be a JSON array"
        raise TypeError(msg)
    return [_source_from_raw(item) for item in parsed if isinstance(item, dict)]


def _source_from_document(source: NewsSource) -> NewsSourceConfig:
    """Convert a stored source document into an ingest config."""
    default_themes = (
        [source.category] if source.category in ALLOWED_NEWS_TAGS else ["world"]
    )
    return _source_from_raw(
        {
            "name": source.name,
            "feed_url": source.feed_url,
            "id": source.id,
            "enabled": source.enabled,
            "default_themes": default_themes,
            "language": "en",
            "etag": source.etag,
            "last_modified": source.last_modified,
        }
    )


def _feed_entries(root: Element) -> list[Element]:
    """Collect RSS/RDF items or Atom entries by local name."""
    local = _local_name(root.tag)
    if local == "feed":
        entries = root.findall("./{*}entry")
        return entries or root.findall(".//{*}entry")
    items = root.findall("./{*}channel/{*}item")
    if items:
        return items
    return root.findall(".//{*}item")


def _entries_to_items(entries: list[Element], source: NewsSourceConfig) -> list[FeedItem]:
    """Normalize RSS/Atom entry elements into FeedItem values."""
    items: list[FeedItem] = []
    for entry in entries:
        title = _clean_text(_child_text(entry, "title"), max_length=255)
        link = _clean_text(_item_link(entry), max_length=1_000)
        if not title or not link:
            continue
        canonical_url = _canonical_url(link, base_url=source.feed_url)
        if not is_public_http_url(canonical_url):
            continue
        items.append(
            FeedItem(
                title=title,
                url=canonical_url,
                excerpt=_item_excerpt(entry),
                published_at=_item_published(entry),
            )
        )
    return items


def parse_feed(xml_text: str, source: NewsSourceConfig) -> list[FeedItem]:
    """Parse common RSS/Atom XML into feed items."""
    if has_unsafe_xml_declaration(xml_text):
        msg = "Feed XML DTD and entity declarations are not supported"
        raise ValueError(msg)
    try:
        root = parse_xml(xml_text)
    except (ParseError, DefusedXmlException, ValueError) as exc:
        msg = "Invalid feed XML"
        raise ValueError(msg) from exc
    # ponytail: namespace-tolerant stdlib path covers common RSS/Atom/RDF; add a
    # source adapter only if a high-value publisher still fails.
    local = _local_name(root.tag)
    if local in {"rss", "RDF", "rdf", "feed"}:
        return _entries_to_items(_feed_entries(root), source)
    return []


def decode_feed_body(content: bytes, *, fallback_encoding: str | None = None) -> str:
    """Prefer the XML encoding declaration over the HTTP charset when present."""
    match = _XML_ENCODING_RE.search(content[:200])
    if match:
        encoding = match.group(1).decode("ascii", errors="ignore")
        try:
            return content.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            pass
    encoding = fallback_encoding or "utf-8"
    try:
        return content.decode(encoding)
    except (LookupError, UnicodeDecodeError):
        return content.decode("utf-8", errors="replace")


def _hash_input(source: NewsSourceConfig, item: FeedItem) -> str:
    """Hash the AI input for repeat processing detection."""
    raw = "|".join([source.name, item.url, item.title, item.excerpt])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _validate_ai_payload(
    raw: dict[str, Any], source: NewsSourceConfig
) -> dict[str, Any]:
    """Validate and normalize the AI JSON response."""
    title = _clean_text(str(raw.get("title", "")), max_length=90)
    summary = _clean_text(str(raw.get("summary", "")), max_length=600)
    bullets = [
        _clean_text(str(item), max_length=180)
        for item in raw.get("bullets", [])
        if isinstance(item, str) and _clean_text(item, max_length=180)
    ][:5]
    tags = [
        tag
        for tag in raw.get("tags", [])
        if isinstance(tag, str) and tag in ALLOWED_NEWS_TAGS
    ][:4]
    if not title or not summary or len(bullets) < 2:
        msg = "AI news summary is incomplete"
        raise ValueError(msg)
    return {
        "title": title,
        "summary": summary,
        "bullets": bullets,
        "tags": tags or list(source.default_themes),
    }


async def _summarize_item(
    source: NewsSourceConfig,
    item: FeedItem,
) -> dict[str, Any]:
    """Summarize one feed item with Groq."""
    settings = get_settings()
    api_key = groq_api_key()
    if not api_key:
        raise ApiError(503, "Groq API key is not configured")
    user_content = json.dumps(
        {
            "source_name": source.name,
            "source_url": item.url,
            "original_title": item.title,
            "feed_excerpt": item.excerpt,
            "published_at": item.published_at.isoformat()
            if item.published_at
            else None,
            "allowed_tags": sorted(ALLOWED_NEWS_TAGS),
            "default_themes": list(source.default_themes),
        },
        ensure_ascii=False,
    )
    parsed = await complete_json(
        api_key=api_key,
        model=settings.GROQ_CHAT_MODEL,
        system_prompt=_SYSTEM_PROMPT,
        user_content=user_content,
        temperature=0.1,
        api_base_url=settings.GROQ_API_BASE_URL,
    )
    return _validate_ai_payload(parsed, source)


def _conditional_headers(source: NewsSourceConfig) -> dict[str, str]:
    """Build feed request headers including conditional GET validators."""
    headers = dict(_FEED_HEADERS)
    if source.etag:
        headers["If-None-Match"] = source.etag
    if source.last_modified:
        headers["If-Modified-Since"] = source.last_modified
    return headers


async def _read_feed_bytes(response: httpx.Response) -> bytes:
    """Read a streamed feed body, aborting when it exceeds the size cap."""
    content_length = response.headers.get("content-length")
    if content_length is not None:
        try:
            declared = int(content_length)
        except ValueError:
            declared = None
        else:
            if declared > _MAX_FEED_BYTES:
                msg = "Feed response is too large"
                raise ValueError(msg)
    chunks: list[bytes] = []
    total = 0
    async for chunk in response.aiter_bytes():
        total += len(chunk)
        if total > _MAX_FEED_BYTES:
            msg = "Feed response is too large"
            raise ValueError(msg)
        chunks.append(chunk)
    return b"".join(chunks)


class NewsIngestService:
    """Fetch trusted feeds and create curated news articles."""

    def __init__(self, news_svc: NewsService) -> None:
        """Initialize the ingestion service."""
        self.news_svc = news_svc

    async def _load_sources(
        self,
        source_ids: list[int] | None,
    ) -> list[NewsSourceConfig]:
        """Load DB-managed sources, falling back to settings JSON when empty."""
        if self.news_svc.registry.news_sources is not None:
            stored_sources = await self.news_svc.list_all_sources()
            if source_ids:
                allowed_ids = set(source_ids)
                stored_sources = [
                    source for source in stored_sources if source.id in allowed_ids
                ]
            if stored_sources or source_ids:
                return [_source_from_document(source) for source in stored_sources]
        return load_news_sources()

    async def _record_fetch(
        self,
        source: NewsSourceConfig,
        *,
        last_error: str | None = None,
        etag: str | None = None,
        last_modified: str | None = None,
        clear_error: bool = False,
    ) -> None:
        """Persist fetch metadata when the source is DB-backed."""
        if source.id is None:
            return
        await self.news_svc.record_source_fetch(
            source.id,
            last_error=last_error,
            etag=etag,
            last_modified=last_modified,
            clear_error=clear_error,
        )

    async def _fetch_items(
        self,
        client: httpx.AsyncClient,
        source: NewsSourceConfig,
    ) -> list[FeedItem] | None:
        """Fetch and parse one feed. Return None when the feed is unchanged (304)."""
        if not is_public_http_url(source.feed_url):
            raise ValueError("Feed URL is not allowed")
        response = await get_public_http_url(
            client,
            source.feed_url,
            headers=_conditional_headers(source),
            stream=True,
        )
        try:
            if response.status_code == 304:
                await self._record_fetch(source, clear_error=True)
                return None
            response.raise_for_status()
            if not is_public_http_url(str(response.url)):
                raise ValueError("Feed redirect target is not allowed")
            content = await _read_feed_bytes(response)
            xml_text = decode_feed_body(content, fallback_encoding=response.encoding)
            items = parse_feed(xml_text, source)[: source.max_items_per_run]
            await self._record_fetch(
                source,
                clear_error=True,
                etag=response.headers.get("etag"),
                last_modified=response.headers.get("last-modified"),
            )
            return items
        finally:
            await response.aclose()

    async def ingest(
        self,
        *,
        actor_id: int | None = None,
        source_ids: list[int] | None = None,
    ) -> NewsIngestResponse:
        """Run ingestion for all enabled sources."""
        settings = get_settings()
        sources = [
            source for source in await self._load_sources(source_ids) if source.enabled
        ]
        processed = created = skipped = failed = 0
        remaining = max(1, settings.NEWS_INGEST_MAX_ITEMS_PER_RUN)
        async with httpx.AsyncClient(timeout=15) as client:
            for source in sources:
                if remaining <= 0:
                    break
                try:
                    items = await self._fetch_items(client, source)
                except Exception as exc:
                    failed += 1
                    await self._record_fetch(source, last_error=str(exc)[:500])
                    logger.warning(
                        "News feed ingest failed",
                        context={"source": source.name, "error": str(exc)[:200]},
                    )
                    continue
                if items is None:
                    continue
                for item in items:
                    if remaining <= 0:
                        break
                    processed += 1
                    if await self.news_svc._news().source_url_exists(item.url):
                        skipped += 1
                        continue
                    try:
                        ai = await _summarize_item(source, item)
                        article = await self.news_svc.create_article(
                            NewsArticleCreate(
                                source_id=source.id,
                                source_name=source.name,
                                source_url=item.url,
                                source_feed_url=source.feed_url,
                                source_published_at=item.published_at,
                                original_title=item.title,
                                title=ai["title"],
                                summary=ai["summary"],
                                bullets=ai["bullets"],
                                tags=ai["tags"],
                                language=source.language,
                                status="published",
                                ai_model=settings.GROQ_CHAT_MODEL,
                                ai_input_hash=_hash_input(source, item),
                            ),
                            actor_id=actor_id,
                        )
                        if (
                            settings.NEWS_TELEGRAM_BOT_TOKEN
                            and settings.NEWS_TELEGRAM_CHANNEL_ID
                        ):
                            from app.workers.tasks import publish_news_telegram_task

                            await asyncio.to_thread(
                                publish_news_telegram_task.delay,
                                article.id,
                            )
                        created += 1
                        remaining -= 1
                    except Exception as exc:
                        failed += 1
                        logger.warning(
                            "News item ingest failed",
                            context={
                                "source": source.name,
                                "url": item.url,
                                "error": str(exc)[:200],
                            },
                        )
        return NewsIngestResponse(
            processed=processed,
            created=created,
            skipped=skipped,
            failed=failed,
        )
