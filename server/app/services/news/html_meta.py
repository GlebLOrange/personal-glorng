"""HTML title parsing and URL/host helpers for news metadata."""

import html
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit

from app.core.exceptions import ValidationError
from app.core.text import sanitize_fetched_text
from app.core.url_safety import is_public_http_url

_METADATA_MAX_BYTES = 200_000
_METADATA_TIMEOUT_SECONDS = 5.0


class _TitleParser(HTMLParser):
    """Extract page title metadata from a small HTML document."""

    def __init__(self) -> None:
        """Initialize title collection state."""
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.meta_titles: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Capture title and common metadata tags."""
        if tag.lower() == "title":
            self.in_title = True
            return
        if tag.lower() != "meta":
            return
        attr_map = {key.lower(): value for key, value in attrs if value}
        name = (attr_map.get("property") or attr_map.get("name") or "").lower()
        if name in {"og:title", "twitter:title"} and attr_map.get("content"):
            self.meta_titles.append(attr_map["content"])

    def handle_endtag(self, tag: str) -> None:
        """Stop title capture after the closing title tag."""
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        """Append text inside the title tag."""
        if self.in_title:
            self.title_parts.append(data)

    def best_title(self) -> str | None:
        """Return the best extracted title."""
        title = NewsHtmlMeta.clean_metadata_text(
            " ".join(self.title_parts), max_length=90
        )
        if title:
            return title
        for value in self.meta_titles:
            title = NewsHtmlMeta.clean_metadata_text(value, max_length=90)
            if title:
                return title
        return None


class NewsHtmlMeta:
    """URL, host, and title helpers used by news services."""

    @staticmethod
    def require_public_feed_url(feed_url: str) -> None:
        """Reject feed URLs that could target local infrastructure."""
        if not is_public_http_url(feed_url):
            raise ValidationError("Feed URL must be a public http(s) URL")

    @staticmethod
    def canonical_url(value: str) -> str:
        """Normalize URL casing and remove fragments."""
        parts = urlsplit(value.strip())
        return urlunsplit(
            (
                parts.scheme.lower(),
                parts.netloc.lower(),
                parts.path or "/",
                parts.query,
                "",
            )
        )

    @staticmethod
    def normalized_host(value: str) -> str:
        """Return a stable source host for a URL."""
        parsed = urlsplit(value)
        if not parsed.hostname:
            raise ValidationError("Article URL must include a host")
        host = parsed.hostname.rstrip(".").lower()
        if host.startswith("www."):
            host = host[4:]
        return host

    @staticmethod
    def homepage_url(value: str) -> str:
        """Return a source homepage URL from an article URL."""
        parts = urlsplit(value)
        host = parts.hostname or ""
        return urlunsplit((parts.scheme.lower(), host.lower(), "/", "", ""))

    @staticmethod
    def source_name_from_host(host: str) -> str:
        """Build a readable source name from a host."""
        labels = host.split(".")
        stem = labels[0] if labels else host
        return (
            " ".join(part.capitalize() for part in re.split(r"[-_]+", stem) if part)
            or host
        )

    @staticmethod
    def clean_metadata_text(value: str | None, *, max_length: int) -> str:
        """Normalize fetched metadata text."""
        if not value:
            return ""
        return sanitize_fetched_text(html.unescape(value), max_length=max_length)

    @staticmethod
    def extract_title(document: str) -> str | None:
        """Extract title metadata from HTML."""
        parser = _TitleParser()
        parser.feed(document)
        return parser.best_title()
