from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from pydantic import ValidationError

from app.schemas.viddownload import VidDownloadRequest, is_allowed_viddownload_host


def test_allowed_viddownload_hosts() -> None:
    assert is_allowed_viddownload_host("https://www.youtube.com/watch?v=abc")
    assert is_allowed_viddownload_host("https://youtu.be/abc")
    assert is_allowed_viddownload_host("https://vimeo.com/123")
    assert is_allowed_viddownload_host("https://player.vimeo.com/video/123")
    assert not is_allowed_viddownload_host("https://example.com/watch?v=abc")


def test_viddownload_schema_rejects_non_allowlisted_public_host() -> None:
    with pytest.raises(ValidationError, match="allowed video platform"):
        VidDownloadRequest(url="https://example.com/watch?v=abc")


@pytest.mark.asyncio
async def test_viddownload_rejects_private_host(auth_client: AsyncClient) -> None:
    """Private/local URLs stay blocked for SSRF prevention."""
    resp = await auth_client.post(
        "/api/tools/vid-download",
        json={
            "url": "https://127.0.0.1/video",
            "format": "best",
            "audio_only": False,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_viddownload_rejects_non_allowlisted_host(
    auth_client: AsyncClient,
) -> None:
    resp = await auth_client.post(
        "/api/tools/vid-download",
        json={
            "url": "https://example.com/watch?v=abc",
            "format": "best",
            "audio_only": False,
        },
    )
    assert resp.status_code == 422
    assert "allowed video platform" in resp.json()["detail"].lower()


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
async def test_viddownload_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/vid-download",
        json={
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "format": "best",
        },
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_viddownload_allowlisted_url_reaches_yt_dlp(
    auth_client: AsyncClient,
) -> None:
    """Allowlisted public URLs pass schema checks; yt-dlp failure returns 502."""
    with (
        patch(
            "app.routers.tools.viddownload._resolve_public_download_url",
            new_callable=AsyncMock,
            return_value="https://www.youtube.com/watch?v=abc",
        ),
        patch(
            "app.routers.tools.viddownload._run_download",
            new_callable=AsyncMock,
            return_value=(b"", b"mock failure", 1),
        ),
    ):
        resp = await auth_client.post(
            "/api/tools/vid-download",
            json={
                "url": "https://www.youtube.com/watch?v=abc",
                "format": "best",
                "audio_only": False,
            },
        )

    assert resp.status_code == 502
    assert "yt-dlp failed" in resp.json()["detail"]
