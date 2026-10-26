"""Tests for news article repository list ordering."""

import json
from datetime import UTC, date, datetime, timedelta

import pytest

from app.db.documents.news import NewsArticle
from app.db.registry import DatabaseRegistry


def _article(
    *,
    slug: str,
    title: str,
    source_published_at: datetime,
    published_at: datetime,
    tags: list[str] | None = None,
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
        tags=json.dumps(tags or ["world"]),
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


@pytest.mark.asyncio
async def test_list_articles_filters_by_tag_and_date_range(
    registry: DatabaseRegistry,
) -> None:
    """Public list filters match tag JSON and inclusive source_published_at bounds."""
    assert registry.news is not None
    mid = datetime(2026, 7, 15, 12, 0, tzinfo=UTC)
    await registry.news.insert(
        _article(
            slug="tech-mid",
            title="Tech mid",
            source_published_at=mid,
            published_at=mid,
            tags=["tech", "world"],
        ),
    )
    await registry.news.insert(
        _article(
            slug="world-old",
            title="World old",
            source_published_at=mid - timedelta(days=10),
            published_at=mid,
            tags=["world"],
        ),
    )
    await registry.news.insert(
        _article(
            slug="tech-new",
            title="Tech new",
            source_published_at=mid + timedelta(days=2),
            published_at=mid,
            tags=["tech"],
        ),
    )

    by_tag = await registry.news.list_articles(status="published", tag="tech", limit=10)
    by_range = await registry.news.list_articles(
        status="published",
        date_from=date(2026, 7, 15),
        date_to=date(2026, 7, 15),
        limit=10,
    )

    assert [article.title for article in by_tag] == ["Tech new", "Tech mid"]
    assert [article.title for article in by_range] == ["Tech mid"]
