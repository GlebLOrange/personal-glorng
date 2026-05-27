from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class VidDownloadRequest(BaseModel):
    url: HttpUrl
    format: str = Field("best", max_length=100)
    audio_only: bool = False
    extra_args: str | None = Field(None, max_length=500)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com/video",
                "format": "best",
                "audio_only": False,
                "extra_args": None,
            }
        }
    )
