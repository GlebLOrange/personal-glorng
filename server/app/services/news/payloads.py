"""JSON list, slug, and payload builders for news articles and sources."""

import json
import re
from typing import Any

from pymongo.errors import DuplicateKeyError

from app.core.exceptions import ValidationError
from app.core.json_lists import parse_json_string_list
from app.core.utils import utc_now
from app.db.documents.news import NewsArticle, NewsSource
from app.schemas.news import (
    NewsArticleCreate,
    NewsArticleUpdate,
    NewsSourceCreate,
)
from app.services.news.html_meta import NewsHtmlMeta

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_SLUG_RETRY_LIMIT = 5


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


def _article_source_fields(
    data: NewsArticleCreate,
    source: NewsSource | None,
) -> dict[str, str | int | None]:
    """Return article source fields from a selected source or payload."""
    source_name = source.name if source else data.source_name
    source_feed_url = (
        source.feed_url
        if source
        else (str(data.source_feed_url) if data.source_feed_url else None)
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
        "tags": _dumps_json_list([str(tag) for tag in data.tags]),
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
    for field in ("bullets", "tags"):
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
    NewsHtmlMeta.require_public_feed_url(feed_url)
    host = data.host or NewsHtmlMeta.normalized_host(feed_url)
    return {
        "name": data.name,
        "feed_url": feed_url,
        "host": host,
        "category": data.category,
        "region": data.region,
        "enabled": data.enabled,
    }
