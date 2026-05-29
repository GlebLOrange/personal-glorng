from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class VidDownloadRequest(BaseModel):
    url: HttpUrl
    format: str = Field("best", max_length=100)
    audio_only: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com/video",
                "format": "best",
                "audio_only": False,
            }
        }
    )
