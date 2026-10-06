"""SSRF hardening for vid-download redirect resolution."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_viddownload_rejects_unsafe_redirect_target(
    auth_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Redirect hops re-run url_safety; private final targets are rejected."""
    monkeypatch.setattr("app.schemas.viddownload.is_public_http_url", lambda _url: True)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.url = httpx.URL("http://127.0.0.1/internal")
    mock_response.is_redirect = False
    mock_response.aclose = AsyncMock()

    with patch(
        "app.routers.tools.viddownload.get_public_http_url",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        resp = await auth_client.post(
            "/api/tools/vid-download",
            json={
                "url": "https://www.youtube.com/watch?v=abc",
                "format": "best",
                "audio_only": False,
            },
        )

    assert resp.status_code == 422
    assert "public http" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_viddownload_rejects_redirect_off_allowlist(
    auth_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Final hop must stay on an allowlisted video host."""
    monkeypatch.setattr("app.schemas.viddownload.is_public_http_url", lambda _url: True)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.url = httpx.URL("https://example.com/bounce")
    mock_response.is_redirect = False
    mock_response.aclose = AsyncMock()

    with (
        patch(
            "app.routers.tools.viddownload.get_public_http_url",
            new_callable=AsyncMock,
            return_value=mock_response,
        ),
        patch(
            "app.routers.tools.viddownload.is_public_http_url",
            return_value=True,
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

    assert resp.status_code == 422
    assert "allowed video platform" in resp.json()["detail"].lower()
