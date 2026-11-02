"""AI summarization helpers for news ingestion."""

import hashlib
import json
from typing import Any

from app.core.exceptions import ApiError
from app.schemas.news import (
    ALLOWED_NEWS_TAGS,
)
from app.services.llm_json import complete_json, groq_api_key
from app.services.news_ingest.feed_parse import (
    FeedItem,
    NewsSourceConfig,
    _clean_text,
)
from app.settings import get_settings

_SYSTEM_PROMPT = """You write concise curated news summaries.
Use only facts present in the supplied feed metadata.
Return JSON with: title, summary, bullets, tags, telegram_text.
Do not invent details. Keep attribution neutral and do not copy publisher prose."""


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


def _feed_only_payload(
    source: NewsSourceConfig,
    item: FeedItem,
) -> dict[str, Any]:
    """Build a publishable payload from feed metadata when Groq is unset."""
    title = _clean_text(item.title, max_length=90) or "Untitled"
    summary = _clean_text(item.excerpt, max_length=600) or title
    detail = _clean_text(item.excerpt, max_length=180) or (
        "See the original article for details."
    )
    return {
        "title": title,
        "summary": summary,
        "bullets": [_clean_text(item.title, max_length=180) or title, detail],
        "tags": list(source.default_themes),
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
        task="news",
        temperature=0.1,
        api_base_url=settings.GROQ_API_BASE_URL,
    )
    return _validate_ai_payload(parsed, source)
