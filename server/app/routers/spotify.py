import json

import httpx
from fastapi import APIRouter, Depends

from app.core.logging import logger
from app.core.rate_limit import rate_limit_api
from app.core.redis import cache_get, cache_set
from app.schemas.spotify import SpotifyNowPlayingResponse
from app.services.spotify import fetch_playback_state, is_spotify_enabled

router = APIRouter(dependencies=[Depends(rate_limit_api)])

_NOW_PLAYING_CACHE_KEY = "spotify:now-playing"
_NOW_PLAYING_CACHE_TTL = 30


@router.get("/now-playing", response_model=SpotifyNowPlayingResponse)
async def now_playing() -> SpotifyNowPlayingResponse:
    if not is_spotify_enabled():
        return SpotifyNowPlayingResponse(enabled=False, is_playing=False)

    cached = await cache_get(_NOW_PLAYING_CACHE_KEY)
    if cached:
        payload = json.loads(cached)
        return SpotifyNowPlayingResponse(enabled=True, **payload)

    try:
        state = await fetch_playback_state()
    except (httpx.HTTPError, RuntimeError) as exc:
        logger.warning(
            "Spotify playback fetch failed",
            context={"error": str(exc)},
        )
        return SpotifyNowPlayingResponse(
            enabled=True,
            is_playing=False,
            error="unavailable",
        )

    await cache_set(
        _NOW_PLAYING_CACHE_KEY,
        json.dumps(state),
        ttl=_NOW_PLAYING_CACHE_TTL,
    )
    return SpotifyNowPlayingResponse(enabled=True, **state)
