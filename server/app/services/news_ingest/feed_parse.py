"""RSS/Atom feed parsing for news ingestion."""

import html
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from xml.etree.ElementTree import Element, ParseError

from defusedxml.common import DefusedXmlException

from app.core.text import sanitize_fetched_text
from app.core.url_safety import is_public_http_url
from app.core.xml_security import has_unsafe_xml_declaration, parse_xml
from app.db.documents.news import NewsSource
from app.schemas.news import (
    ALLOWED_NEWS_TAGS,
)
from app.settings import get_settings

_TAG_RE = re.compile(r"<[^>]+>")
_XML_ENCODING_RE = re.compile(
    rb"<\?xml[^>]*encoding=['\"]([^'\"]+)['\"]",
    re.IGNORECASE,
)
_MAX_FEED_BYTES = 1_000_000
# ponytail: DW-only allowlist; drop this skip when adding a second publisher.
DW_FEED_URL = "https://rss.dw.com/xml/rss-en-all"
DW_SOURCE_NAME = "DW"
DW_HOST = "dw.com"
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
    """Strip HTML tags, then sanitize control chars and whitespace."""
    if not value:
        return ""
    text = html.unescape(_TAG_RE.sub(" ", value))
    return sanitize_fetched_text(text, max_length=max_length)


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


def _entries_to_items(
    entries: list[Element], source: NewsSourceConfig
) -> list[FeedItem]:
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
        except LookupError, UnicodeDecodeError:
            pass
    encoding = fallback_encoding or "utf-8"
    try:
        return content.decode(encoding)
    except LookupError, UnicodeDecodeError:
        return content.decode("utf-8", errors="replace")
