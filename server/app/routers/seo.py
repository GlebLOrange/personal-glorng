"""Public SEO routes (sitemap, robots)."""

from html import escape
from typing import Annotated

from fastapi import APIRouter, Path
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from app.core.exceptions import NotFoundError
from app.db.deps import DbRegistry
from app.services.news_og_html import render_news_og_html
from app.settings import get_settings

router = APIRouter(tags=["seo"])

_PUBLIC_PATHS: tuple[tuple[str, str], ...] = (
    ("/", "weekly"),
    ("/news", "daily"),
    ("/tools", "weekly"),
    ("/privacy", "monthly"),
)


def _public_paths() -> tuple[tuple[str, str], ...]:
    """Static sitemap paths."""
    return _PUBLIC_PATHS


def _url_entry(loc: str, changefreq: str, lastmod: str | None = None) -> str:
    """Build one sitemap <url> block with escaped loc."""
    lines = [
        "  <url>",
        f"    <loc>{escape(loc)}</loc>",
        f"    <changefreq>{changefreq}</changefreq>",
    ]
    if lastmod is not None:
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
    lines.append("  </url>")
    return "\n".join(lines)


@router.get(
    "/sitemap.xml",
    response_class=Response,
    summary="Get sitemap",
    description="Public XML sitemap for search engines.",
)
async def sitemap_xml(registry: DbRegistry) -> Response:
    base = get_settings().BASE_URL.rstrip("/")
    static_urls = [_url_entry(f"{base}{path}", freq) for path, freq in _public_paths()]
    news_urls: list[str] = []
    if registry.news is not None:
        articles = await registry.news.list_articles(status="published", limit=1_000)
        news_urls = [
            _url_entry(
                f"{base}/news/{article.slug}",
                "weekly",
                lastmod=article.updated_at.date().isoformat(),
            )
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


# SPA shells that are noindex / auth-gated — keep crawlers off them.
_ROBOTS_DISALLOW: tuple[str, ...] = (
    "/admin",
    "/api",
    "/callback",
    "/login",
    "/settings",
    "/verify-email",
    "/forgot-password",
    "/reset-password",
)


@router.get(
    "/og/news/{slug}",
    response_class=HTMLResponse,
    include_in_schema=True,
    summary="News article Open Graph HTML",
    description=(
        "Static HTML with OG/Twitter meta for link previews. "
        "Canonical URL points at the SPA route `/news/{slug}`."
    ),
)
async def news_og_html(
    registry: DbRegistry,
    slug: Annotated[str, Path(pattern=r"^[a-z0-9][a-z0-9-]{0,119}$")],
) -> HTMLResponse:
    if registry.news is None:
        raise NotFoundError("Article not found")
    article = await registry.news.get_by_slug(slug)
    if article is None or article.status != "published":
        raise NotFoundError("Article not found")
    html = render_news_og_html(article, base_url=get_settings().BASE_URL)
    return HTMLResponse(content=html)


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
        *[f"Disallow: {path}" for path in _ROBOTS_DISALLOW],
        f"Sitemap: {base}/sitemap.xml",
    ]
    return PlainTextResponse("\n".join(lines) + "\n")
