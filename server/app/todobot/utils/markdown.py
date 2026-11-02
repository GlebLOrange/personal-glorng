"""Telegram Markdown (legacy) escaping for user-controlled strings."""


def escape_md(value: str | None) -> str:
    """Escape characters that break Telegram legacy Markdown parse_mode."""
    if not value:
        return ""
    # ponytail: legacy Markdown specials; MarkdownV2 escape if parse_mode changes.
    for ch in ("\\", "*", "_", "`", "["):
        value = value.replace(ch, f"\\{ch}")
    return value
