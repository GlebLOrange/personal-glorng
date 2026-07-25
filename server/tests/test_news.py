from datetime import UTC, datetime

import pytest

from app.db.documents.news import NewsArticle
from app.db.registry import DatabaseRegistry
from app.schemas.news import NewsArticleCreate
from app.services.audit import AuditService
from app.services.news import NewsService


def _article(*, slug: str, title: str, status: str) -> NewsArticle:
    """Build a minimal news article for service tests."""
    published_at = datetime(2026, 6, 27, tzinfo=UTC)
    return NewsArticle(
        slug=slug,
        status=status,  # type: ignore[arg-type]
        source_name="Example",
        source_url=f"https://example.com/{slug}",
        source_feed_url="https://example.com/rss.xml",
        original_title=title,
        title=title,
        summary="Summary",
        themes='["tech"]',
        published_at=published_at if status == "published" else None,
    )


@pytest.mark.asyncio
async def test_public_news_only_returns_published_articles(
    registry: DatabaseRegistry,
) -> None:
    """Public news ignores non-published enabled articles."""
    assert registry.news is not None
    service = NewsService(registry, AuditService(registry))
    await registry.news.insert(
        _article(slug="visible", title="Visible", status="published"),
    )
    await registry.news.insert(
        _article(slug="draft", title="Draft", status="draft"),
    )

    response = await service.list_articles(status="published")

    assert [article.title for article in response.items] == ["Visible"]


@pytest.mark.asyncio
async def test_create_article_persists_required_fields(
    registry: DatabaseRegistry,
) -> None:
    """create_article stores required fields and returns them."""
    assert registry.news is not None
    service = NewsService(registry, AuditService(registry))
    payload = NewsArticleCreate(
        source_name="Metadata Source",
        source_url="https://example.com/story",
        source_feed_url="https://example.com/rss.xml",
        original_title="Metadata title",
        title="Metadata title",
        summary="Metadata summary",
        themes=["tech"],
        status="draft",
    )

    article = await service.create_article(payload)

    assert article.title == "Metadata title"
    assert article.summary == "Metadata summary"
    assert article.source_name == "Metadata Source"
    assert article.slug
