import re
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.core.url_safety import is_public_http_url

_FORMAT_PATTERN = re.compile(r"^[a-zA-Z0-9+._/\[\]<=\s-]{1,100}$")

# Host roots allowed for yt-dlp (exact match or subdomain).
_ALLOWED_VID_HOST_ROOTS = frozenset({"youtube.com", "youtu.be", "vimeo.com"})


def is_allowed_viddownload_host(url: str) -> bool:
    """Return True when the URL host is an allowlisted video platform."""
    host = urlparse(url).hostname
    if not host:
        return False
    host = host.lower().rstrip(".")
    return host in _ALLOWED_VID_HOST_ROOTS or any(
        host.endswith(f".{root}") for root in _ALLOWED_VID_HOST_ROOTS
    )


class VidDownloadRequest(BaseModel):
    url: HttpUrl
    format: str = Field("best", max_length=100)
    audio_only: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "format": "best",
                "audio_only": False,
            }
        }
    )

    @field_validator("format")
    @classmethod
    def validate_format(cls, value: str) -> str:
        if not _FORMAT_PATTERN.match(value):
            msg = "Invalid yt-dlp format string"
            raise ValueError(msg)
        return value

    @field_validator("url")
    @classmethod
    def validate_public_url(cls, value: HttpUrl) -> HttpUrl:
        """Accept allowlisted public http(s) URLs; reject private/local targets."""
        url = str(value)
        if not is_public_http_url(url):
            msg = "URL must be a public http(s) address"
            raise ValueError(msg)
        if not is_allowed_viddownload_host(url):
            msg = "URL host is not an allowed video platform"
            raise ValueError(msg)
        return value
