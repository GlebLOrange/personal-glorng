"""Minimal HTML with Open Graph tags for shareable resume profile previews."""

from __future__ import annotations

from html import escape

from app.schemas.resume import ResumeProfileSelection
from app.services.resume_export import profile_seo_description, profile_seo_title


def render_profile_og_html(
    selection: ResumeProfileSelection,
    *,
    base_url: str,
    query: str = "",
) -> str:
    """Return a small HTML document with OG/Twitter meta for a filtered profile."""
    origin = base_url.rstrip("/")
    path = f"/profile?{query}" if query else "/profile"
    canonical = f"{origin}{path}"
    title = escape(profile_seo_title(selection))
    description = escape(profile_seo_description(selection))
    image = f"{origin}/social-preview.png"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <link rel="canonical" href="{escape(canonical)}" />
  <meta property="og:type" content="profile" />
  <meta property="og:site_name" content="Gleb.Y" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:url" content="{escape(canonical)}" />
  <meta property="og:image" content="{image}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{description}" />
  <meta name="twitter:image" content="{image}" />
</head>
<body>
  <p><a href="{escape(canonical)}">{title}</a></p>
</body>
</html>
"""
