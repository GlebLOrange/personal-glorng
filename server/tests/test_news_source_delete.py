"""Tests for deleting news sources that still have articles."""

import pytest

from app.db.documents.news import NewsArticle, NewsSource
from app.db.registry import DatabaseRegistry
from app.services.audit import AuditService
from app.services.news import NewsService


@pytest.mark.asyncio
async def test_delete_source_detaches_articles(registry: DatabaseRegistry) -> None:
    """Deleting a source clears article FKs and keeps denormalized source text."""
    assert registry.news is not None
    assert registry.news_sources is not None
    service = NewsService(registry, AuditService(registry))

    source = await registry.news_sources.insert(
        NewsSource(
            name="Example News",
            feed_url="https://example.com/rss.xml",
            host="example.com",
            category="world",
            region="global",
        )
    )
    article = await registry.news.insert(
        NewsArticle(
            slug="example-headline",
            status="published",
            source_id=source.id,
            source_name="Example News",
            source_url="https://example.com/story",
            source_feed_url="https://example.com/rss.xml",
            original_title="Example headline",
            title="Example headline",
            summary="Summary",
        )
    )

    await service.delete_source(source.id)

    assert await registry.news_sources.get_or_none(source.id) is None
    refreshed = await registry.news.get(article.id)
    assert refreshed is not None
    assert refreshed.source_id is None
    assert refreshed.source_name == "Example News"
