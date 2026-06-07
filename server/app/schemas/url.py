from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.core.url_safety import validate_redirect_url


class UrlCreate(BaseModel):
    original_url: HttpUrl
    title: str | None = Field(None, max_length=255)

    @field_validator("original_url")
    @classmethod
    def validate_safe_url(cls, value: HttpUrl) -> HttpUrl:
        validate_redirect_url(str(value))
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_url": "https://example.com/very-long-url",
                "title": "Example Site",
            }
        }
    )


class UrlResponse(BaseModel):
    id: int
    code: str
    original_url: str
    title: str | None
    clicks: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "code": "aBcD1234",
                "original_url": "https://example.com/very-long-url",
                "title": "Example Site",
                "clicks": 42,
                "created_at": "2026-05-25T03:00:00Z",
            }
        },
    )
