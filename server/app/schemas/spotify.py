from pydantic import BaseModel, ConfigDict


class SpotifyNowPlayingResponse(BaseModel):
    enabled: bool
    is_playing: bool
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    album_art_url: str | None = None
    track_url: str | None = None
    progress_ms: int | None = None
    duration_ms: int | None = None
    error: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "enabled": True,
                "is_playing": True,
                "title": "Example Track",
                "artist": "Example Artist",
                "album": "Example Album",
                "album_art_url": "https://i.scdn.co/image/example",
                "track_url": "https://open.spotify.com/track/example",
                "progress_ms": 45000,
                "duration_ms": 180000,
            }
        }
    )
