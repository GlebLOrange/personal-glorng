import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.services.spotify import fetch_playback_state, is_spotify_enabled

_SPOTIFY_DISABLED_SETTINGS = SimpleNamespace(
    SPOTIFY_CLIENT_ID="",
    SPOTIFY_CLIENT_SECRET="",
    SPOTIFY_REFRESH_TOKEN="",
)


@pytest.mark.asyncio
async def test_now_playing_disabled_when_unconfigured(client: AsyncClient) -> None:
    with (
        patch(
            "app.routers.spotify.is_spotify_enabled",
            return_value=False,
        ),
        patch(
            "app.services.spotify.get_settings",
            return_value=_SPOTIFY_DISABLED_SETTINGS,
        ),
    ):
        resp = await client.get("/api/spotify/now-playing")

    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is False
    assert data["is_playing"] is False


@pytest.mark.asyncio
async def test_now_playing_response_shape(client: AsyncClient) -> None:
    with (
        patch("app.routers.spotify.is_spotify_enabled", return_value=True),
        patch(
            "app.routers.spotify.fetch_playback_state",
            new_callable=AsyncMock,
            return_value={
                "is_playing": True,
                "title": "Test Song",
                "artist": "Test Artist",
                "album": "Test Album",
                "album_art_url": "https://i.scdn.co/image/test",
                "track_url": "https://open.spotify.com/track/abc",
                "progress_ms": 1000,
                "duration_ms": 200000,
            },
        ),
    ):
        resp = await client.get("/api/spotify/now-playing")

    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is True
    assert data["is_playing"] is True
    assert data["title"] == "Test Song"
    assert data["artist"] == "Test Artist"
    assert "refresh_token" not in json.dumps(data).lower()
    assert "client_secret" not in json.dumps(data).lower()


@pytest.mark.asyncio
async def test_now_playing_idle(client: AsyncClient) -> None:
    with (
        patch("app.routers.spotify.is_spotify_enabled", return_value=True),
        patch(
            "app.routers.spotify.fetch_playback_state",
            new_callable=AsyncMock,
            return_value={"is_playing": False},
        ),
    ):
        resp = await client.get("/api/spotify/now-playing")

    data = resp.json()
    assert data["enabled"] is True
    assert data["is_playing"] is False


@pytest.mark.asyncio
async def test_now_playing_unavailable_on_error(client: AsyncClient) -> None:
    with (
        patch("app.routers.spotify.is_spotify_enabled", return_value=True),
        patch(
            "app.routers.spotify.fetch_playback_state",
            new_callable=AsyncMock,
            side_effect=RuntimeError("token failed"),
        ),
    ):
        resp = await client.get("/api/spotify/now-playing")

    data = resp.json()
    assert data["enabled"] is True
    assert data["is_playing"] is False
    assert data["error"] == "unavailable"


@pytest.mark.asyncio
async def test_is_spotify_enabled_requires_all_credentials() -> None:
    with patch(
        "app.services.spotify.get_settings",
        return_value=type(
            "S",
            (),
            {
                "SPOTIFY_CLIENT_ID": "id",
                "SPOTIFY_CLIENT_SECRET": "",
                "SPOTIFY_REFRESH_TOKEN": "rt",
            },
        )(),
    ):
        assert is_spotify_enabled() is False


@pytest.mark.asyncio
async def test_fetch_playback_state_parses_track() -> None:
    token_resp = MagicMock()
    token_resp.status_code = 200
    token_resp.json.return_value = {"access_token": "test-token"}

    playing_resp = MagicMock()
    playing_resp.status_code = 200
    playing_resp.json.return_value = {
        "is_playing": True,
        "progress_ms": 5000,
        "item": {
            "name": "Song",
            "duration_ms": 180000,
            "artists": [{"name": "Artist A"}, {"name": "Artist B"}],
            "album": {
                "name": "Album",
                "images": [
                    {"url": "https://large.example", "height": 640},
                    {"url": "https://small.example", "height": 64},
                ],
            },
            "external_urls": {"spotify": "https://open.spotify.com/track/1"},
        },
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = token_resp
    mock_client.get.return_value = playing_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with (
        patch("app.services.spotify.get_settings") as mock_settings,
        patch("app.services.spotify.httpx.AsyncClient", return_value=mock_client),
    ):
        mock_settings.return_value = type(
            "S",
            (),
            {
                "SPOTIFY_CLIENT_ID": "id",
                "SPOTIFY_CLIENT_SECRET": "secret",
                "SPOTIFY_REFRESH_TOKEN": "refresh",
            },
        )()
        state = await fetch_playback_state()

    assert state["is_playing"] is True
    assert state["title"] == "Song"
    assert state["artist"] == "Artist A, Artist B"
    assert state["album_art_url"] == "https://small.example"
    assert state["track_url"] == "https://open.spotify.com/track/1"
