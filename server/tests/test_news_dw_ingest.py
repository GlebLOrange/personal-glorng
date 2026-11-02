"""DW-only news ingest helpers and source allowlist."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.db.documents.news import NewsArticle, NewsSource
from app.db.registry import DatabaseRegistry
from app.services.audit import AuditService
from app.services.news import NewsService
from app.services.news_ingest import (
    DW_FEED_URL,
    DW_HOST,
    DW_SOURCE_NAME,
    FeedItem,
    NewsIngestService,
    NewsSourceConfig,
    _feed_only_payload,
)


@pytest.mark.asyncio
async def test_prepare_dw_only_repairs_feed_and_disables_others(
    registry: DatabaseRegistry,
) -> None:
    """Ingest prep keeps only Deutsche Welle English RSS enabled."""
    assert registry.news_sources is not None
    assert registry.news is not None
    bbc = await registry.news_sources.insert(
        NewsSource(
            name="BBC News",
            feed_url="https://www.bbc.com/",
            host="bbc.com",
            enabled=True,
        )
    )
    dw = await registry.news_sources.insert(
        NewsSource(
            name=DW_SOURCE_NAME,
            feed_url="https://www.dw.com/",
            host=DW_HOST,
            enabled=False,
        )
    )
    await registry.news.insert(
        NewsArticle(
            slug="demo-news-1",
            status="published",
            source_name=DW_SOURCE_NAME,
            source_url="https://www.dw.com/demo/1",
            source_feed_url="https://www.dw.com/",
            original_title="Demo",
            title="Demo",
            summary="Demo summary",
            ai_model="demo",
        )
    )

    service = NewsIngestService(NewsService(registry, AuditService(registry)))
    await service._prepare_dw_only()

    updated_dw = await registry.news_sources.get(dw.id)
    updated_bbc = await registry.news_sources.get(bbc.id)
    demo = await registry.news.get_by_slug("demo-news-1")

    assert updated_dw is not None
    assert updated_dw.enabled is True
    assert updated_dw.feed_url == DW_FEED_URL
    assert updated_bbc is not None
    assert updated_bbc.enabled is False
    assert demo is not None
    assert demo.status == "draft"


def test_feed_only_payload_uses_feed_metadata() -> None:
    """Without Groq, publish the feed title, excerpt, and default tags."""
    source = NewsSourceConfig(
        name=DW_SOURCE_NAME,
        feed_url=DW_FEED_URL,
        default_themes=("world",),
    )
    item = FeedItem(
        title="DW headline",
        url="https://www.dw.com/en/story",
        excerpt="Short excerpt from the RSS item.",
        published_at=datetime(2026, 10, 26, tzinfo=UTC),
    )

    payload = _feed_only_payload(source, item)

    assert payload["title"] == "DW headline"
    assert payload["summary"] == "Short excerpt from the RSS item."
    assert payload["tags"] == ["world"]
    assert len(payload["bullets"]) >= 2
