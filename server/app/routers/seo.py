"""Public SEO routes (sitemap, robots)."""

from html import escape

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

from app.db.deps import DbRegistry
from app.settings import get_settings

router = APIRouter(tags=["seo"])

_PUBLIC_PATHS: tuple[tuple[str, str], ...] = (
    ("/", "weekly"),
    ("/news", "daily"),
    ("/privacy", "monthly"),
)


@router.get(
    "/sitemap.xml",
    response_class=Response,
    summary="Get sitemap",
    description="Public XML sitemap for search engines.",
)
async def sitemap_xml(registry: DbRegistry) -> Response:
    base = get_settings().BASE_URL.rstrip("/")
    static_urls = [
        f"  <url>\n"
        f"    <loc>{base}{path}</loc>\n"
        f"    <changefreq>{freq}</changefreq>\n"
        f"  </url>"
        for path, freq in _PUBLIC_PATHS
    ]
    news_urls: list[str] = []
    if registry.news is not None:
        articles = await registry.news.list_articles(status="published", limit=1_000)
        news_urls = [
            f"  <url>\n"
            f"    <loc>{escape(f'{base}/news/{article.slug}')}</loc>\n"
            f"    <changefreq>weekly</changefreq>\n"
            f"    <lastmod>{article.updated_at.date().isoformat()}</lastmod>\n"
            f"  </url>"
            for article in articles
        ]
    urls = "\n".join(static_urls + news_urls)
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
    return Response(content=body, media_type="application/xml")


@router.get(
    "/robots.txt",
    response_class=PlainTextResponse,
    summary="Get robots.txt",
    description="Public robots.txt for crawlers.",
)
async def robots_txt() -> PlainTextResponse:
    base = get_settings().BASE_URL.rstrip("/")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin",
        "Disallow: /api",
        "Disallow: /callback",
        f"Sitemap: {base}/sitemap.xml",
    ]
    return PlainTextResponse("\n".join(lines) + "\n")
