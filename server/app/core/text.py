"""Shared text normalization and sanitization."""

import re

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def normalize_whitespace(text: str) -> str:
    """Collapse repeated whitespace to single spaces."""
    return " ".join(text.split())


def sanitize_text(text: str, *, max_length: int | None = None) -> str:
    """Strip control chars, normalize whitespace, and optionally truncate."""
    cleaned = normalize_whitespace(_CONTROL_CHAR_RE.sub("", text.strip()))
    if max_length is not None:
        return cleaned[:max_length]
    return cleaned


def sanitize_optional_text(
    text: str | None,
    *,
    max_length: int | None = None,
) -> str | None:
    """Sanitize optional text; return None when empty after cleaning."""
    if text is None:
        return None
    cleaned = sanitize_text(text, max_length=max_length)
    return cleaned or None
