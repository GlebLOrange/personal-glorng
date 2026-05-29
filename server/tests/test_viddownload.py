from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_viddownload_rejects_disallowed_host(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/vid-download",
        json={
            "url": "https://example.com/video",
            "format": "best",
            "audio_only": False,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_viddownload_rejects_invalid_format(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/vid-download",
        json={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "format": "best;rm -rf /",
            "audio_only": False,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_viddownload_unauthorized(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/vid-download",
        json={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "format": "best",
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_viddownload_youtube_url_passes_validation(
    auth_client: AsyncClient,
) -> None:
    """Valid YouTube URLs pass schema checks; yt-dlp failure returns 502."""
    with patch(
        "app.routers.tools.viddownload._run_download",
        new_callable=AsyncMock,
        return_value=(b"", b"mock failure", 1),
    ):
        resp = await auth_client.post(
            "/api/tools/vid-download",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "format": "best",
                "audio_only": False,
            },
        )

    assert resp.status_code == 502
    assert "yt-dlp failed" in resp.json()["detail"]
