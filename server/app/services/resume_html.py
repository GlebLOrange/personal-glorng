"""Shared HTML fragments for the resume PDF and AMP page."""

from __future__ import annotations

import base64
import html
from functools import lru_cache
from pathlib import Path
from typing import Any

_BRAND_LOGO_PNG = (
    Path(__file__).resolve().parents[1] / "static" / "brand" / "gy-logo-512.png"
)

CONTACT_ORDER = ("email", "telegram", "linkedin", "github")


def escape_text(value: str) -> str:
    """Escape plain text for safe HTML output."""
    return html.escape(value, quote=True)


@lru_cache(maxsize=1)
def resume_brand_logo_data_uri() -> str:
    """Inline PNG for WeasyPrint (no external fetch)."""
    encoded = base64.standard_b64encode(_BRAND_LOGO_PNG.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def resume_brand_logo_html() -> str:
    """Brand mark for printable resume header."""
    src = escape_text(resume_brand_logo_data_uri())
    alt = escape_text("Gleb.Y")
    return f'<img class="brand-logo" src="{src}" alt="{alt}" />'


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
