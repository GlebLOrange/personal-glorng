from datetime import UTC, datetime

import pytest

from app.db.documents.news import NewsArticle, NewsSource
from app.db.registry import DatabaseRegistry
from app.schemas.news import NewsArticleCreate
from app.services.news import NewsService, normalize_feed_articles


async def _noop_cache_invalidator() -> None:
    """Avoid touching Redis in focused news service tests."""


def test_normalize_feed_articles_parses_rss_entry() -> None:
    """RSS entries are normalized into stored feed article documents."""
    source = NewsSource(
        name="Example News",
        feed_url="https://example.com/rss.xml",
        category="world",
        region="global",
    )
    feed = b"""
    <rss version="2.0">
      <channel>
        <item>
          <title>Example headline</title>
          <link>/story/example-headline</link>
          <description><![CDATA[<p>Short summary</p>]]></description>
          <pubDate>Sat, 27 Jun 2026 04:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    articles = normalize_feed_articles(feed, source)

    assert len(articles) == 1
    assert articles[0].title == "Example headline"
    assert articles[0].link == "https://example.com/story/example-headline"
    assert articles[0].summary == "Short summary"
    assert articles[0].status == "published"


@pytest.mark.asyncio
async def test_public_news_only_returns_published_articles(
    registry: DatabaseRegistry,
) -> None:
    """Public news ignores non-published enabled articles."""
    assert registry.news_articles is not None
    service = NewsService(registry, cache_invalidator=_noop_cache_invalidator)
    published_at = datetime(2026, 6, 27, tzinfo=UTC)
    await registry.news_articles.insert(
        NewsArticle(
            title="Visible",
            link="https://example.com/visible",
            source="Example",
            status="published",
            published_at=published_at,
        ),
    )
    await registry.news_articles.insert(
        NewsArticle(
            title="Draft",
            link="https://example.com/draft",
            source="Example",
            status="draft",
            published_at=published_at,
        ),
    )

    response = await service.get_public_news()

    assert [article.title for article in response.articles] == ["Visible"]


@pytest.mark.asyncio
async def test_create_article_fills_blank_fields_from_metadata(
    registry: DatabaseRegistry,
) -> None:
    """Blank article fields can be filled by the injected metadata fetcher."""
    assert registry.news_articles is not None

    async def metadata_fetcher(_link: str) -> dict[str, str]:
        """Return deterministic article metadata."""
        return {
            "title": "Metadata title",
            "summary": "Metadata summary",
            "source": "Metadata Source",
        }

    payload = NewsArticleCreate(
        title="",
        link="https://example.com/story",
        source="",
        published_at=datetime(2026, 6, 27, tzinfo=UTC),
    ).model_dump()
    service = NewsService(
        registry,
        metadata_fetcher=metadata_fetcher,
        cache_invalidator=_noop_cache_invalidator,
    )

    article = await service.create_article(payload)

    assert article.title == "Metadata title"
    assert article.summary == "Metadata summary"
    assert article.source == "Metadata Source"
