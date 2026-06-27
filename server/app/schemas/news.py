import re
from datetime import datetime
from typing import Literal
from urllib.parse import unquote, urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from app.core.url_safety import validate_redirect_url
from app.schemas.validators import validate_clean_optional, validate_clean_required

_TITLE_MARKER_RE = re.compile(r"\{\{([^{}]+)\}\}")
_SOURCE_HOST_MARKER_RE = re.compile(r"(?:^|\.)\{\{([^{}]+)\}\}(?=\.|(?::\d+)?$)")
_DW_ARTICLE_SLUG_RE = re.compile(r"/en/([^/?#]+)/a-\d+")
_SOURCE_HOST_PREFIXES = {"www", "rss", "feeds", "feed", "news", "m", "amp"}
_SOURCE_ALIASES = {
    "bbc": "BBC News",
    "bbci": "BBC News",
    "dw": "DW",
    "deutschewelle": "DW",
    "reutersagency": "Reuters",
    "theguardian": "The Guardian",
    "aljazeera": "Al Jazeera",
    "france24": "France 24",
    "japantimes": "The Japan Times",
    "abc": "ABC Australia",
    "nytimes": "New York Times",
    "nyt": "New York Times",
}
NewsArticleStatus = Literal["draft", "moderating", "published", "archived"]
NewsArticleSortField = Literal["published_at", "created_at", "updated_at"]
SortOrder = Literal["asc", "desc"]


def _title_from_slug(slug: str) -> str | None:
    """Return a title-cased article title from a URL slug."""
    words = re.sub(r"[^a-zA-Z0-9]+", " ", unquote(slug)).split()
    if not words:
        return None
    return " ".join(word[:1].upper() + word[1:].lower() for word in words)[:180]


def _source_from_slug(slug: str) -> str | None:
    """Return a display source name from a URL host marker."""
    alias = _SOURCE_ALIASES.get(news_source_key(slug))
    if alias is not None:
        return alias
    title = _title_from_slug(slug)
    if title is None:
        return None
    return " ".join(
        word.upper() if len(word) <= 3 else word for word in title.split()
    )[:120]


def news_source_key(value: str) -> str:
    """Return a stable key for comparing editable news source names."""
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _source_slug_from_netloc(netloc: str) -> str | None:
    """Return the likely source slug from a URL host."""
    match = _SOURCE_HOST_MARKER_RE.search(netloc)
    if match is not None:
        return match.group(1)
    host = netloc.rsplit("@", 1)[-1].split(":", 1)[0].strip().lower()
    labels = [label for label in host.split(".") if label]
    for label in labels:
        if label not in _SOURCE_HOST_PREFIXES:
            return label
    return None


def title_from_news_article_link(link: str) -> str | None:
    """Return a title-cased article title from an admin news URL."""
    parsed = urlparse(link)
    match = _TITLE_MARKER_RE.search(parsed.path)
    if match is not None:
        return _title_from_slug(match.group(1))

    dw_slug = _DW_ARTICLE_SLUG_RE.search(parsed.path)
    if dw_slug is not None:
        return _title_from_slug(dw_slug.group(1))
    for segment in reversed(parsed.path.split("/")):
        slug = segment.rsplit(".", 1)[0].strip()
        title = _title_from_slug(slug)
        if title is not None:
            return title
    host = (parsed.hostname or parsed.netloc).removeprefix("www.")
    if host:
        return _title_from_slug(host.split(".", 1)[0])
    return None


def source_from_news_article_link(link: str) -> str | None:
    """Return a source name from a marked or normal URL host."""
    parsed = urlparse(link)
    slug = _source_slug_from_netloc(parsed.netloc)
    if slug is None:
        return None
    return _source_from_slug(slug)


def source_from_news_source_url(url: str) -> str | None:
    """Return a source name from a marked or normal RSS source URL host."""
    return source_from_news_article_link(url)


def source_home_url_from_news_article_link(link: str) -> str | None:
    """Return a source homepage URL from an article URL."""
    parsed = urlparse(sanitize_news_article_link(link))
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None
    labels = [label for label in parsed.hostname.lower().split(".") if label]
    while len(labels) > 2 and labels[0] in _SOURCE_HOST_PREFIXES:
        labels.pop(0)
    if not labels:
        return None
    return f"{parsed.scheme}://{'.'.join(labels)}"


def sanitize_news_article_link(link: str) -> str:
    """Remove admin title markers from a news article URL path."""
    return _TITLE_MARKER_RE.sub(lambda match: match.group(1).strip(), link)


def sanitize_news_source_url(url: str) -> str:
    """Remove admin source markers from an RSS source URL."""
    return _TITLE_MARKER_RE.sub(lambda match: match.group(1).strip(), url)


class NewsSourceBase(BaseModel):
    """Shared input fields for RSS source management."""

    name: str = Field(min_length=1, max_length=120)
    feed_url: HttpUrl
    category: str = Field(default="world", min_length=1, max_length=64)
    region: str = Field(default="global", min_length=1, max_length=64)
    enabled: bool = True

    @model_validator(mode="before")
    @classmethod
    def fill_name_from_feed_url_marker(cls, value: object) -> object:
        """Derive a blank source name from a marked RSS feed URL."""
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        if str(payload.get("name") or "").strip():
            return payload
        source = source_from_news_source_url(str(payload.get("feed_url") or ""))
        if source is not None:
            payload["name"] = source
        return payload

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        """Normalize source display names."""
        return validate_clean_required(value, max_length=120, field_name="Name")

    @field_validator("feed_url", mode="before")
    @classmethod
    def clean_feed_url_marker(cls, value: object) -> object:
        """Strip source markers before URL validation/storage."""
        return sanitize_news_source_url(str(value))

    @field_validator("category", "region")
    @classmethod
    def clean_label(cls, value: str) -> str:
        """Normalize source labels."""
        return validate_clean_required(value, max_length=64, field_name="Label")


class NewsSourceCreate(NewsSourceBase):
    """Create a managed RSS source."""


class NewsSourceUpdate(BaseModel):
    """Patch fields for a managed RSS source."""

    name: str | None = Field(None, min_length=1, max_length=120)
    feed_url: HttpUrl | None = None
    category: str | None = Field(None, min_length=1, max_length=64)
    region: str | None = Field(None, min_length=1, max_length=64)
    enabled: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def fill_name_from_feed_url_marker(cls, value: object) -> object:
        """Derive a provided blank source name from a marked RSS feed URL."""
        if (
            not isinstance(value, dict)
            or "name" not in value
            or str(value.get("name") or "").strip()
        ):
            return value
        source = source_from_news_source_url(str(value.get("feed_url") or ""))
        if source is None:
            return value
        return {**value, "name": source}

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        """Normalize optional source display names."""
        if value is None:
            return None
        return validate_clean_required(value, max_length=120, field_name="Name")

    @field_validator("feed_url", mode="before")
    @classmethod
    def clean_feed_url_marker(cls, value: object) -> object:
        """Strip source markers before URL validation/storage."""
        if value is None:
            return None
        return sanitize_news_source_url(str(value))

    @field_validator("category", "region")
    @classmethod
    def clean_label(cls, value: str | None) -> str | None:
        """Normalize optional labels."""
        if value is None:
            return None
        return validate_clean_required(value, max_length=64, field_name="Label")


class NewsSourceResponse(BaseModel):
    """RSS source returned to admin clients."""

    id: int
    name: str
    feed_url: str
    category: str
    region: str
    enabled: bool
    last_error: str | None
    last_fetched_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NewsSourcesRefreshRequest(BaseModel):
    """Optional source selection for manual RSS parsing."""

    source_ids: list[int] | None = Field(None, max_length=500)

    @field_validator("source_ids")
    @classmethod
    def clean_source_ids(cls, value: list[int] | None) -> list[int] | None:
        """Normalize selected RSS source ids."""
        if value is None:
            return None
        cleaned = list(dict.fromkeys(value))
        if any(source_id <= 0 for source_id in cleaned):
            raise ValueError("Source ids must be positive integers")
        return cleaned or None


class NewsArticleResponse(BaseModel):
    """Normalized article from a third-party feed."""

    id: str
    title: str
    link: str
    source: str
    category: str
    region: str
    summary: str | None = None
    published_at: datetime | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    editable: bool = False

    @field_validator("summary")
    @classmethod
    def clean_summary(cls, value: str | None) -> str | None:
        """Trim feed summaries before returning them."""
        return validate_clean_optional(value, max_length=500)


class NewsArticleCreate(BaseModel):
    """Create an admin-curated news article."""

    title: str = Field(default="", max_length=180)
    link: HttpUrl
    source_feed_url: HttpUrl | None = None
    source: str = Field(default="gLOrng", max_length=120)
    status: NewsArticleStatus = "moderating"
    category: str = Field(default="world", min_length=1, max_length=64)
    region: str = Field(default="global", min_length=1, max_length=64)
    summary: str | None = Field(None, max_length=500)
    published_at: datetime
    enabled: bool = True

    @model_validator(mode="before")
    @classmethod
    def fill_fields_from_link_marker(cls, value: object) -> object:
        """Derive blank source names from marked URLs."""
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        raw_link = str(payload.get("link") or "")
        source = str(payload.get("source") or "").strip()
        if not source or source == "gLOrng":
            derived_source = source_from_news_article_link(raw_link)
            if derived_source is not None:
                payload["source"] = derived_source
        return payload

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        """Normalize article titles."""
        return validate_clean_optional(value, max_length=180) or ""

    @field_validator("link", mode="before")
    @classmethod
    def clean_link_marker(cls, value: object) -> object:
        """Strip title markers before URL validation/storage."""
        return sanitize_news_article_link(str(value))

    @field_validator("link")
    @classmethod
    def validate_safe_link(cls, value: HttpUrl) -> HttpUrl:
        """Reject article links that are unsafe to render as public outbound URLs."""
        validate_redirect_url(str(value))
        return value

    @field_validator("source_feed_url", mode="before")
    @classmethod
    def clean_source_feed_url_marker(cls, value: object) -> object:
        """Strip source markers before source URL validation."""
        if value is None:
            return None
        return sanitize_news_source_url(str(value))

    @field_validator("source")
    @classmethod
    def clean_source(cls, value: str) -> str:
        """Normalize article source names."""
        return validate_clean_optional(value, max_length=120) or ""

    @field_validator("category", "region")
    @classmethod
    def clean_article_label(cls, value: str) -> str:
        """Normalize article labels."""
        return validate_clean_required(value, max_length=64, field_name="Label")

    @field_validator("summary")
    @classmethod
    def clean_article_summary(cls, value: str | None) -> str | None:
        """Normalize article summaries."""
        return validate_clean_optional(value, max_length=500)


class NewsArticleUpdate(BaseModel):
    """Patch fields for an admin-curated news article."""

    title: str | None = Field(None, max_length=180)
    link: HttpUrl | None = None
    source_feed_url: HttpUrl | None = None
    source: str | None = Field(None, max_length=120)
    status: NewsArticleStatus | None = None
    category: str | None = Field(None, min_length=1, max_length=64)
    region: str | None = Field(None, min_length=1, max_length=64)
    summary: str | None = Field(None, max_length=500)
    published_at: datetime | None = None
    enabled: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def fill_fields_from_link_marker(cls, value: object) -> object:
        """Derive provided blank source names from marked URLs."""
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        raw_link = str(payload.get("link") or "")
        source = str(payload.get("source") or "").strip()
        if "source" in payload and (not source or source == "gLOrng"):
            derived_source = source_from_news_article_link(raw_link)
            if derived_source is not None:
                payload["source"] = derived_source
        return payload

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        """Normalize optional article titles."""
        if value is None:
            return None
        return validate_clean_optional(value, max_length=180) or ""

    @field_validator("link", mode="before")
    @classmethod
    def clean_link_marker(cls, value: object) -> object:
        """Strip title markers before URL validation/storage."""
        if value is None:
            return None
        return sanitize_news_article_link(str(value))

    @field_validator("link")
    @classmethod
    def validate_safe_link(cls, value: HttpUrl | None) -> HttpUrl | None:
        """Reject article links that are unsafe to render as public outbound URLs."""
        if value is None:
            return None
        validate_redirect_url(str(value))
        return value

    @field_validator("source_feed_url", mode="before")
    @classmethod
    def clean_source_feed_url_marker(cls, value: object) -> object:
        """Strip source markers before source URL validation."""
        if value is None:
            return None
        return sanitize_news_source_url(str(value))

    @field_validator("source")
    @classmethod
    def clean_source(cls, value: str | None) -> str | None:
        """Normalize optional source names."""
        if value is None:
            return None
        return validate_clean_optional(value, max_length=120) or ""

    @field_validator("category", "region")
    @classmethod
    def clean_article_label(cls, value: str | None) -> str | None:
        """Normalize optional labels."""
        if value is None:
            return None
        return validate_clean_required(value, max_length=64, field_name="Label")

    @field_validator("summary")
    @classmethod
    def clean_article_summary(cls, value: str | None) -> str | None:
        """Normalize optional article summaries."""
        return validate_clean_optional(value, max_length=500)


class NewsArticleAdminResponse(BaseModel):
    """Curated article returned to admin clients."""

    id: int
    title: str
    link: str
    source: str
    origin: str
    status: str
    category: str
    region: str
    summary: str | None
    published_at: datetime
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NewsListResponse(BaseModel):
    """Public news response."""

    articles: list[NewsArticleResponse]
    sources: list[str]
    categories: list[str]
    regions: list[str]
    page: int
    per_page: int
    total: int
    pages: int
    updated_at: datetime
