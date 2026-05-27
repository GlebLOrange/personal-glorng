"""Spotify Web API client for currently-playing playback."""

from typing import Any

import httpx

from app.core.logging import logger
from app.core.redis import cache_get, cache_set
from app.settings import get_settings

_SPOTIFY_OAUTH_URL = "https://accounts.spotify.com/api/token"
_CURRENTLY_PLAYING_URL = "https://api.spotify.com/v1/me/player/currently-playing"
_SPOTIFY_ACCESS_CACHE_KEY = "spotify:access_token"
_SPOTIFY_ACCESS_CACHE_TTL = 3500


def is_spotify_enabled() -> bool:
    settings = get_settings()
    return bool(
        settings.SPOTIFY_CLIENT_ID
        and settings.SPOTIFY_CLIENT_SECRET
        and settings.SPOTIFY_REFRESH_TOKEN
    )


async def get_access_token() -> str:
    cached = await cache_get(_SPOTIFY_ACCESS_CACHE_KEY)
    if cached:
        return cached

    settings = get_settings()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            _SPOTIFY_OAUTH_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": settings.SPOTIFY_REFRESH_TOKEN,
            },
            auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )

    if resp.status_code != 200:
        logger.error(
            "Spotify token refresh failed",
            context={"status": resp.status_code},
        )
        msg = "Failed to refresh Spotify access token"
        raise RuntimeError(msg)

    data = resp.json()
    token = data.get("access_token")
    if not token:
        logger.error("Spotify token response missing access_token")
        msg = "Spotify token response invalid"
        raise RuntimeError(msg)

    await cache_set(_SPOTIFY_ACCESS_CACHE_KEY, token, ttl=_SPOTIFY_ACCESS_CACHE_TTL)
    return token


def _artist_names(item: dict[str, Any]) -> str:
    artists = item.get("artists") or []
    return ", ".join(a.get("name", "") for a in artists if a.get("name"))


def _album_art_url(item: dict[str, Any]) -> str | None:
    album = item.get("album") or {}
    images = album.get("images") or []
    if not images:
        return None
    return images[-1].get("url")


def _parse_playing_payload(data: dict[str, Any]) -> dict[str, Any]:
    item = data.get("item") or {}
    return {
        "is_playing": True,
        "title": item.get("name"),
        "artist": _artist_names(item),
        "album": (item.get("album") or {}).get("name"),
        "album_art_url": _album_art_url(item),
        "track_url": (item.get("external_urls") or {}).get("spotify"),
        "progress_ms": data.get("progress_ms"),
        "duration_ms": item.get("duration_ms"),
    }


async def fetch_playback_state() -> dict[str, Any]:
    """Return playback fields; idle when nothing is playing."""
    token = await get_access_token()

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            _CURRENTLY_PLAYING_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )

    if resp.status_code == 204:
        return {"is_playing": False}

    if resp.status_code != 200:
        logger.warning(
            "Spotify currently-playing request failed",
            context={"status": resp.status_code},
        )
        return {"is_playing": False, "error": "unavailable"}

    data = resp.json()
    if not data.get("is_playing"):
        return {"is_playing": False}

    return _parse_playing_payload(data)
