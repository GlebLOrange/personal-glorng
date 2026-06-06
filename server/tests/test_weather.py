from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.services.weather import SITE_CITY_KEY
from tests.conftest import FakeRedis

WEATHER_PAYLOAD = {
    "current_condition": [{"temp_C": "20", "humidity": "50", "windspeedKmph": "10"}],
    "nearest_area": [
        {
            "areaName": [{"value": "London"}],
            "country": [{"value": "United Kingdom"}],
        }
    ],
}


def _mock_weather_client(payload: dict | None = None) -> MagicMock:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = payload or WEATHER_PAYLOAD

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


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
    with patch(
        "app.services.weather.httpx.AsyncClient",
        return_value=_mock_weather_client({"current_condition": [{"temp_C": "20"}]}),
    ):
        resp = await auth_client.get("/api/tools/weather/London")

    assert resp.status_code == 200
    assert resp.json()["current_condition"][0]["temp_C"] == "20"


@pytest.mark.asyncio
async def test_weather_config_public_default(client: AsyncClient) -> None:
    resp = await client.get("/api/weather/config")
    assert resp.status_code == 200
    assert resp.json()["city"] == "Wroclaw"


@pytest.mark.asyncio
async def test_weather_current_public(client: AsyncClient) -> None:
    with patch(
        "app.services.weather.httpx.AsyncClient",
        return_value=_mock_weather_client(),
    ):
        resp = await client.get("/api/weather/current")

    assert resp.status_code == 200
    assert resp.json()["nearest_area"][0]["areaName"][0]["value"] == "London"


@pytest.mark.asyncio
async def test_set_display_city_requires_auth(client: AsyncClient) -> None:
    resp = await client.put("/api/tools/weather/city", json={"city": "Krakow"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_set_display_city_updates_config(
    auth_client: AsyncClient,
    fake_redis: FakeRedis,
) -> None:
    try:
        with patch(
            "app.services.weather.httpx.AsyncClient",
            return_value=_mock_weather_client(),
        ):
            put_resp = await auth_client.put(
                "/api/tools/weather/city",
                json={"city": "Krakow"},
            )
            assert put_resp.status_code == 200
            assert put_resp.json()["city"] == "Krakow"

            config_resp = await auth_client.get("/api/weather/config")
            assert config_resp.status_code == 200
            assert config_resp.json()["city"] == "Krakow"

            current_resp = await auth_client.get("/api/weather/current")
            assert current_resp.status_code == 200
    finally:
        await fake_redis.delete(SITE_CITY_KEY)


@pytest.mark.asyncio
async def test_set_display_city_invalid(auth_client: AsyncClient) -> None:
    resp = await auth_client.put(
        "/api/tools/weather/city",
        json={"city": "Paris123"},
    )
    assert resp.status_code == 422
    assert "invalid" in resp.json()["detail"].lower()
