"""Shared HTML fragments for the resume PDF and AMP page."""

from __future__ import annotations

import html
from typing import Any

CONTACT_ORDER = ("email", "telegram", "linkedin", "github")


def escape_text(value: str) -> str:
    """Escape plain text for safe HTML output."""
    return html.escape(value, quote=True)


def contact_href(link_id: str, raw: str) -> str:
    """Return the href target for a resume contact link."""
    if link_id == "email":
        return f"mailto:{raw}"
    return raw


def highlights_html(highlights: list[Any]) -> str:
    """Render bullet highlights when valid strings are present."""
    items = [
        escape_text(str(item)) for item in highlights if isinstance(item, str) and item
    ]
    if not items:
        return ""
    bullets = "".join(f"<li>{item}</li>" for item in items)
    return f'<ul class="highlights">{bullets}</ul>'
