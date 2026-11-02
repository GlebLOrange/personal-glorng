"""Trusted RSS/Atom ingestion for curated news."""

from app.services.news_ingest.ai_summarize import (
    _SYSTEM_PROMPT,
    _feed_only_payload,
    _hash_input,
    _summarize_item,
    _validate_ai_payload,
)
from app.services.news_ingest.feed_parse import (
    DW_FEED_URL,
    DW_HOST,
    DW_SOURCE_NAME,
    FeedItem,
    NewsSourceConfig,
    _canonical_url,
    decode_feed_body,
    load_news_sources,
    parse_feed,
)
from app.services.news_ingest.service import NewsIngestService

__all__ = [
    "DW_FEED_URL",
    "DW_HOST",
    "DW_SOURCE_NAME",
    "_SYSTEM_PROMPT",
    "FeedItem",
    "NewsIngestService",
    "NewsSourceConfig",
    "_canonical_url",
    "_feed_only_payload",
    "_hash_input",
    "_summarize_item",
    "_validate_ai_payload",
    "decode_feed_body",
    "load_news_sources",
    "parse_feed",
]
