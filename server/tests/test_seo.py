from datetime import UTC, datetime

import pytest
from httpx import AsyncClient

from app.db.documents.news import NewsArticle
from app.db.registry import DatabaseRegistry


@pytest.mark.asyncio
async def test_sitemap_xml(client: AsyncClient) -> None:
    resp = await client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert "application/xml" in resp.headers["content-type"]
    body = resp.text
    assert "<loc>http://localhost/</loc>" in body
    assert "<loc>http://localhost/privacy</loc>" in body
    assert "<loc>http://localhost/tools</loc>" in body
    assert "<loc>http://localhost/news</loc>" in body
    assert "<loc>http://localhost/calculator</loc>" not in body
    assert "<loc>http://localhost/weather</loc>" not in body
    assert "/admin" not in body


def _published_article(*, slug: str) -> NewsArticle:
    return NewsArticle(
        slug=slug,
        status="published",
        source_name="Example",
        source_url=f"https://example.com/{slug}",
        source_feed_url="https://example.com/rss.xml",
        original_title="OG headline",
        title="OG headline",
        summary="Curated summary for previews.",
        tags='["tech"]',
        published_at=datetime(2026, 6, 27, tzinfo=UTC),
    )


@pytest.mark.asyncio
async def test_news_og_html_includes_meta(
    client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    assert registry.news is not None
    await registry.news.insert(_published_article(slug="preview-slug"))

    resp = await client.get("/og/news/preview-slug")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    body = resp.text
    assert 'property="og:title"' in body
    assert "OG headline" in body
    assert "Curated summary for previews." in body
    assert "http://localhost/news/preview-slug" in body


@pytest.mark.asyncio
async def test_news_og_html_404_for_draft(
    client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    assert registry.news is not None
    draft = _published_article(slug="draft-only")
    draft.status = "draft"
    await registry.news.insert(draft)

    resp = await client.get("/og/news/draft-only")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_robots_txt(client: AsyncClient) -> None:
    resp = await client.get("/robots.txt")
    assert resp.status_code == 200
    body = resp.text
    assert "Disallow: /admin" in body
    assert "Disallow: /login" in body
    assert "Disallow: /settings" in body
    assert "Sitemap: http://localhost/sitemap.xml" in body
