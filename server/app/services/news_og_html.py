"""Minimal HTML with Open Graph tags for news link previews (non-JS crawlers)."""

from urllib.parse import quote

from app.db.documents.news import NewsArticle
from app.services.og_html import render_og_html


def render_news_og_html(article: NewsArticle, *, base_url: str) -> str:
    """Return a small HTML document with OG/Twitter meta for one published article."""
    origin = base_url.rstrip("/")
    canonical = f"{origin}/news/{quote(article.slug, safe='')}"
    return render_og_html(
        title=article.title,
        description=(article.summary or "").strip()[:500],
        canonical_url=canonical,
        og_type="article",
        image_url=f"{origin}/social-preview.png",
    )
