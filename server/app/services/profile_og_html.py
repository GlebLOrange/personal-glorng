"""Minimal HTML with Open Graph tags for shareable resume profile previews."""

from __future__ import annotations

from app.schemas.resume import ResumeProfileSelection
from app.services.og_html import render_og_html
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
    return render_og_html(
        title=profile_seo_title(selection),
        description=profile_seo_description(selection),
        canonical_url=f"{origin}{path}",
        og_type="profile",
        image_url=f"{origin}/social-preview.png",
    )
