"""Tests for news article repository list ordering."""

from datetime import UTC, datetime, timedelta

import pytest

from app.db.documents.news import NewsArticle
from app.db.registry import DatabaseRegistry


def _article(
    *,
    slug: str,
    title: str,
    source_published_at: datetime,
    published_at: datetime,
) -> NewsArticle:
    """Build a published article with explicit story and digest timestamps."""
    return NewsArticle(
        slug=slug,
        status="published",
        source_name="Example News",
        source_url=f"https://example.com/{slug}",
        source_feed_url="https://example.com/rss.xml",
        source_published_at=source_published_at,
        original_title=title,
        title=title,
        summary="Summary",
        published_at=published_at,
    )


@pytest.mark.asyncio
async def test_list_articles_sorts_by_source_published_at_desc(
    registry: DatabaseRegistry,
) -> None:
    """Published lists prefer original story time over digest publish time."""
    assert registry.news is not None
    newer_story = datetime(2026, 7, 15, 10, 0, tzinfo=UTC)
    older_story = datetime(2026, 7, 14, 10, 0, tzinfo=UTC)
    older_digest = newer_story - timedelta(hours=1)
    newer_digest = newer_story + timedelta(hours=1)

    await registry.news.insert(
        _article(
            slug="older-story-ingested-later",
            title="Older story",
            source_published_at=older_story,
            published_at=newer_digest,
        ),
    )
    await registry.news.insert(
        _article(
            slug="newer-story-ingested-earlier",
            title="Newer story",
            source_published_at=newer_story,
            published_at=older_digest,
        ),
    )

    articles = await registry.news.list_articles(status="published", limit=10)

    assert [article.title for article in articles] == ["Newer story", "Older story"]
