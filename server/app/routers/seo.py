"""Public SEO routes (sitemap, robots)."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

from app.settings import get_settings

router = APIRouter(tags=["seo"])

_PUBLIC_PATHS: tuple[tuple[str, str], ...] = (
    ("/", "weekly"),
    ("/privacy", "monthly"),
)


@router.get("/sitemap.xml", response_class=Response)
async def sitemap_xml() -> Response:
    base = get_settings().BASE_URL.rstrip("/")
    urls = "\n".join(
        f"  <url>\n"
        f"    <loc>{base}{path}</loc>\n"
        f"    <changefreq>{freq}</changefreq>\n"
        f"  </url>"
        for path, freq in _PUBLIC_PATHS
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
    return Response(content=body, media_type="application/xml")


@router.get("/robots.txt", response_class=PlainTextResponse)
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
