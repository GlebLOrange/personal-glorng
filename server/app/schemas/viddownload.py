import re

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.core.url_safety import is_public_http_url

_FORMAT_PATTERN = re.compile(r"^[a-zA-Z0-9+._/\[\]<=\s-]{1,100}$")


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
        """Accept any public http(s) URL; reject private/local targets (SSRF)."""
        if not is_public_http_url(str(value)):
            msg = "URL must be a public http(s) address"
            raise ValueError(msg)
        return value
