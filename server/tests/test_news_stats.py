"""Tests for admin news stats."""

import pytest

from app.db.documents.news import NewsArticle
from app.db.registry import DatabaseRegistry
from app.services.audit import AuditService
from app.services.news import NewsService


def _article(*, slug: str, status: str) -> NewsArticle:
    """Build a minimal news article for stats tests."""
    return NewsArticle(
        slug=slug,
        status=status,  # type: ignore[arg-type]
        source_name="Example News",
        source_url=f"https://example.com/{slug}",
        source_feed_url="https://example.com/rss.xml",
        original_title=f"Title {slug}",
        title=f"Title {slug}",
        summary="Summary",
    )


@pytest.mark.asyncio
async def test_news_stats_counts_by_status(registry: DatabaseRegistry) -> None:
    """Admin stats return totals for each article status."""
    assert registry.news is not None
    service = NewsService(registry, AuditService(registry))

    for slug, status in (
        ("draft-one", "draft"),
        ("published-one", "published"),
        ("published-two", "published"),
        ("unpublished-one", "unpublished"),
        ("failed-one", "failed"),
    ):
        await registry.news.insert(_article(slug=slug, status=status))

    stats = await service.news_stats()

    assert stats.total == 5
    assert stats.draft == 1
    assert stats.published == 2
    assert stats.unpublished == 1
    assert stats.failed == 1
