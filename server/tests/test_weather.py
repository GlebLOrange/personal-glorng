from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_weather_invalid_city(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/tools/weather/Paris123")
    assert resp.status_code == 422
    assert "invalid" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_weather_unauthorized(client: AsyncClient) -> None:
    resp = await client.get("/api/tools/weather/London")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_weather_success(auth_client: AsyncClient) -> None:
    payload = {"current_condition": [{"temp_C": "20"}]}
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = payload

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.weather.httpx.AsyncClient", return_value=mock_client):
        resp = await auth_client.get("/api/tools/weather/London")

    assert resp.status_code == 200
    assert resp.json() == payload
    mock_client.get.assert_awaited_once()
