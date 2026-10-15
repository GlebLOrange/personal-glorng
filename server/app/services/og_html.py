"""Shared minimal Open Graph HTML documents for non-JS crawlers."""

from html import escape


def render_og_html(
    *,
    title: str,
    description: str,
    canonical_url: str,
    og_type: str,
    image_url: str,
) -> str:
    """Return a small HTML document with OG/Twitter meta tags."""
    safe_title = escape(title, quote=True)
    safe_description = escape(description, quote=True)
    safe_canonical = escape(canonical_url, quote=True)
    safe_type = escape(og_type, quote=True)
    safe_image = escape(image_url, quote=True)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{safe_title}</title>
  <meta name="description" content="{safe_description}" />
  <link rel="canonical" href="{safe_canonical}" />
  <meta property="og:type" content="{safe_type}" />
  <meta property="og:site_name" content="Gleb.Y" />
  <meta property="og:title" content="{safe_title}" />
  <meta property="og:description" content="{safe_description}" />
  <meta property="og:url" content="{safe_canonical}" />
  <meta property="og:image" content="{safe_image}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{safe_title}" />
  <meta name="twitter:description" content="{safe_description}" />
  <meta name="twitter:image" content="{safe_image}" />
</head>
<body>
  <p><a href="{safe_canonical}">{safe_title}</a></p>
</body>
</html>
"""
