"""Trusted RSS/Atom ingestion for curated news."""

import asyncio
import hashlib
import html
import ipaddress
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urljoin, urlparse, urlsplit, urlunsplit
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

import httpx

from app.core.exceptions import ApiError
from app.core.logging import logger
from app.db.documents.news import NewsSource
from app.schemas.news import (
    ALLOWED_NEWS_THEMES,
    NewsArticleCreate,
    NewsIngestResponse,
)
from app.services.llm_json import complete_json, openai_api_key
from app.services.news import NewsService
from app.settings import get_settings

_TAG_RE = re.compile(r"<[^>]+>")
_ATOM = "{http://www.w3.org/2005/Atom}"
_CONTENT = "{http://purl.org/rss/1.0/modules/content/}"
_SYSTEM_PROMPT = """You write concise curated news summaries.
Use only facts present in the supplied feed metadata.
Return JSON with: title, summary, bullets, themes, telegram_text.
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


def _canonical_url(value: str, *, base_url: str) -> str:
    """Normalize a feed item URL for dedupe."""
    joined = urljoin(base_url, value.strip())
    parts = urlsplit(joined)
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path, parts.query, ""))


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse common RSS/Atom datetime values."""
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _is_safe_feed_url(url: str) -> bool:
    """Reject obviously unsafe feed URLs."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    try:
        ip = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        return parsed.hostname not in {"localhost", "metadata.google.internal"}
    return not (ip.is_private or ip.is_loopback or ip.is_link_local)


def _source_from_raw(raw: dict[str, Any]) -> NewsSourceConfig:
    """Parse one source config object."""
    name = _clean_text(str(raw.get("name", "")), max_length=120)
    feed_url = str(raw.get("feed_url", "")).strip()
    if not name or not feed_url or not _is_safe_feed_url(feed_url):
        msg = "Invalid news source config"
        raise ValueError(msg)
    themes = tuple(
        theme
        for theme in raw.get("default_themes", ["world"])
        if isinstance(theme, str) and theme in ALLOWED_NEWS_THEMES
    )
    return NewsSourceConfig(
        name=name,
        feed_url=feed_url,
        id=raw.get("id") if isinstance(raw.get("id"), int) else None,
        enabled=bool(raw.get("enabled", True)),
        default_themes=themes or ("world",),
        max_items_per_run=max(1, min(int(raw.get("max_items_per_run", 5)), 20)),
        language=_clean_text(str(raw.get("language", "en")), max_length=12) or "en",
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
        [source.category] if source.category in ALLOWED_NEWS_THEMES else ["world"]
    )
    return _source_from_raw(
        {
            "name": source.name,
            "feed_url": source.feed_url,
            "id": source.id,
            "enabled": source.enabled,
            "default_themes": default_themes,
            "language": "en",
        }
    )


def _rss_items(root: ElementTree.Element, source: NewsSourceConfig) -> list[FeedItem]:
    """Parse RSS items."""
    items: list[FeedItem] = []
    for item in root.findall("./channel/item"):
        title = _clean_text(item.findtext("title"), max_length=255)
        link = _clean_text(item.findtext("link"), max_length=1_000)
        excerpt = _clean_text(
            item.findtext("description") or item.findtext(f"{_CONTENT}encoded"),
        )
        if title and link:
            items.append(
                FeedItem(
                    title=title,
                    url=_canonical_url(link, base_url=source.feed_url),
                    excerpt=excerpt,
                    published_at=_parse_datetime(
                        item.findtext("pubDate") or item.findtext("published")
                    ),
                )
            )
    return items


def _atom_items(root: ElementTree.Element, source: NewsSourceConfig) -> list[FeedItem]:
    """Parse Atom entries."""
    items: list[FeedItem] = []
    for entry in root.findall(f"{_ATOM}entry"):
        title = _clean_text(entry.findtext(f"{_ATOM}title"), max_length=255)
        link = ""
        for node in entry.findall(f"{_ATOM}link"):
            if node.attrib.get("rel", "alternate") == "alternate":
                link = node.attrib.get("href", "")
                break
        excerpt = _clean_text(
            entry.findtext(f"{_ATOM}summary") or entry.findtext(f"{_ATOM}content"),
        )
        if title and link:
            items.append(
                FeedItem(
                    title=title,
                    url=_canonical_url(link, base_url=source.feed_url),
                    excerpt=excerpt,
                    published_at=_parse_datetime(
                        entry.findtext(f"{_ATOM}published")
                        or entry.findtext(f"{_ATOM}updated")
                    ),
                )
            )
    return items


def parse_feed(xml_text: str, source: NewsSourceConfig) -> list[FeedItem]:
    """Parse common RSS/Atom XML into feed items."""
    try:
        root = ElementTree.fromstring(xml_text)  # noqa: S314
    except ParseError as exc:
        msg = "Invalid feed XML"
        raise ValueError(msg) from exc
    # ponytail: stdlib feed parsing covers common RSS/Atom; add source adapters if
    # a high-value publisher uses unusual extensions.
    if root.tag.endswith("rss"):
        return _rss_items(root, source)
    if root.tag == f"{_ATOM}feed":
        return _atom_items(root, source)
    return []


def _hash_input(source: NewsSourceConfig, item: FeedItem) -> str:
    """Hash the AI input for repeat processing detection."""
    raw = "|".join([source.name, item.url, item.title, item.excerpt])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _validate_ai_payload(raw: dict[str, Any], source: NewsSourceConfig) -> dict[str, Any]:
    """Validate and normalize the AI JSON response."""
    title = _clean_text(str(raw.get("title", "")), max_length=90)
    summary = _clean_text(str(raw.get("summary", "")), max_length=600)
    bullets = [
        _clean_text(str(item), max_length=180)
        for item in raw.get("bullets", [])
        if isinstance(item, str) and _clean_text(item, max_length=180)
    ][:5]
    themes = [
        theme
        for theme in raw.get("themes", [])
        if isinstance(theme, str) and theme in ALLOWED_NEWS_THEMES
    ][:4]
    if not title or not summary or len(bullets) < 2:
        msg = "AI news summary is incomplete"
        raise ValueError(msg)
    return {
        "title": title,
        "summary": summary,
        "bullets": bullets,
        "themes": themes or list(source.default_themes),
    }


async def _summarize_item(
    source: NewsSourceConfig,
    item: FeedItem,
) -> dict[str, Any]:
    """Summarize one feed item with an OpenAI-compatible model."""
    settings = get_settings()
    api_key = openai_api_key()
    if not api_key:
        raise ApiError(503, "OpenAI API key is not configured")
    user_content = json.dumps(
        {
            "source_name": source.name,
            "source_url": item.url,
            "original_title": item.title,
            "feed_excerpt": item.excerpt,
            "published_at": item.published_at.isoformat() if item.published_at else None,
            "allowed_themes": sorted(ALLOWED_NEWS_THEMES),
            "default_themes": list(source.default_themes),
        },
        ensure_ascii=False,
    )
    parsed = await complete_json(
        api_key=api_key,
        model=settings.OPENAI_CHAT_MODEL,
        system_prompt=_SYSTEM_PROMPT,
        user_content=user_content,
        temperature=0.1,
        base_url=settings.LLM_BASE_URL or None,
    )
    return _validate_ai_payload(parsed, source)


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
            stored_sources = await self.news_svc.list_sources()
            if source_ids:
                allowed_ids = set(source_ids)
                stored_sources = [
                    source for source in stored_sources if source.id in allowed_ids
                ]
            if stored_sources or source_ids:
                return [_source_from_document(source) for source in stored_sources]
        return load_news_sources()

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
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            for source in sources:
                if remaining <= 0:
                    break
                try:
                    response = await client.get(source.feed_url)
                    response.raise_for_status()
                    items = parse_feed(response.text, source)[: source.max_items_per_run]
                except Exception as exc:
                    failed += 1
                    logger.warning(
                        "News feed ingest failed",
                        context={"source": source.name, "error": str(exc)[:200]},
                    )
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
                                themes=ai["themes"],
                                language=source.language,
                                status="published",
                                ai_model=settings.OPENAI_CHAT_MODEL,
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
