import re
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

_FORMAT_PATTERN = re.compile(r"^[a-zA-Z0-9+._/\[\]<=\s-]{1,100}$")
_ALLOWED_VIDEO_HOSTS = frozenset(
    {
        "youtube.com",
        "youtu.be",
        "m.youtube.com",
        "music.youtube.com",
    }
)


def _normalize_host(hostname: str) -> str:
    host = hostname.lower()
    if host.startswith("www."):
        return host[4:]
    return host


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
    def validate_video_host(cls, value: HttpUrl) -> HttpUrl:
        host = urlparse(str(value)).hostname
        if not host or _normalize_host(host) not in _ALLOWED_VIDEO_HOSTS:
            msg = "URL host is not an allowed video provider"
            raise ValueError(msg)
        return value
