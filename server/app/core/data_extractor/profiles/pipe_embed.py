"""Built-in profile for 13-field pipe-delimited embed feeds."""

from __future__ import annotations

import re
from typing import Any

IFRAME_SRC_RE = re.compile(r"""src=["']([^"']+)["']""", re.IGNORECASE)

PIPE_EMBED_FIELD_NAMES: list[str] = [
    "embed_html",
    "thumb_url",
    "preview_urls",
    "title",
    "tags",
    "categories",
    "performers",
    "channel",
    "duration_sec",
    "view_count",
    "upvote_count",
    "downvote_count",
    "thumb_base_url",
]

PIPE_EMBED_LIST_FIELDS = frozenset(
    {"preview_urls", "tags", "categories", "performers"},
)

_INT_FIELDS = frozenset(
    {"duration_sec", "view_count", "upvote_count", "downvote_count"},
)

_URL_STRING_FIELDS = frozenset({"thumb_url", "thumb_base_url"})


def _clean_url(value: str) -> str:
    return value.replace(" ", "").replace("\n", "").replace("\r", "")


def transform_pipe_embed_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize a parsed pipe-embed row."""
    embed_html = record.get("embed_html", "")
    if isinstance(embed_html, str):
        match = IFRAME_SRC_RE.search(embed_html)
        if match:
            embed_url = _clean_url(match.group(1))
            record["embed_url"] = embed_url
            record["embed_id"] = embed_url.rstrip("/").rsplit("/", maxsplit=1)[-1]

    for key in _URL_STRING_FIELDS:
        value = record.get(key)
        if isinstance(value, str):
            record[key] = _clean_url(value)

    preview_urls = record.get("preview_urls")
    if isinstance(preview_urls, list):
        record["preview_urls"] = [
            _clean_url(item) for item in preview_urls if isinstance(item, str) and item
        ]

    for key in _INT_FIELDS:
        value = record.get(key)
        if isinstance(value, str):
            stripped = value.strip()
            record[key] = int(stripped) if stripped else None

    channel = record.get("channel")
    if channel == "":
        record["channel"] = None

    upvotes = record.get("upvote_count")
    downvotes = record.get("downvote_count")
    total_votes = (
        upvotes + downvotes
        if isinstance(upvotes, int) and isinstance(downvotes, int)
        else 0
    )
    if total_votes > 0:
        record["rating_percent"] = round(100 * upvotes / total_votes, 1)

    return record
