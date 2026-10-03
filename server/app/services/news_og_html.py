"""Minimal HTML with Open Graph tags for news link previews (non-JS crawlers)."""

from html import escape
from urllib.parse import quote

from app.db.documents.news import NewsArticle


def render_news_og_html(article: NewsArticle, *, base_url: str) -> str:
    """Return a small HTML document with OG/Twitter meta for one published article."""
    origin = base_url.rstrip("/")
    canonical = f"{origin}/news/{quote(article.slug, safe='')}"
    title = escape(article.title)
    description = escape((article.summary or "").strip()[:500])
    image = f"{origin}/social-preview.png"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="Gleb.Y" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{image}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{description}" />
  <meta name="twitter:image" content="{image}" />
</head>
<body>
  <p><a href="{canonical}">{title}</a></p>
</body>
</html>
"""
