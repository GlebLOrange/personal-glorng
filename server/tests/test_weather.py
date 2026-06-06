from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

WEATHER_PAYLOAD = {
    "current_condition": [
        {
            "temp_C": "20",
            "humidity": "50",
            "windspeedKmph": "10",
            "localObsDateTime": "2026-06-06 01:00 PM",
        }
    ],
    "nearest_area": [
        {
            "areaName": [{"value": "London"}],
            "country": [{"value": "United Kingdom"}],
        }
    ],
    "time_zone": [{"utcOffset": "+1.0"}],
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
async def test_weather_lookup_invalid_city(client: AsyncClient) -> None:
    resp = await client.get("/api/time-date-weather-location/lookup/Paris123")
    assert resp.status_code == 422
    assert "invalid" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_weather_lookup_public(client: AsyncClient) -> None:
    with patch(
        "app.services.weather.httpx.AsyncClient",
        return_value=_mock_weather_client({"current_condition": [{"temp_C": "20"}]}),
    ):
        resp = await client.get("/api/time-date-weather-location/lookup/London")

    assert resp.status_code == 200
    assert resp.json()["current_condition"][0]["temp_C"] == "20"


@pytest.mark.asyncio
async def test_weather_lookup_coords(client: AsyncClient) -> None:
    with patch(
        "app.services.weather.httpx.AsyncClient",
        return_value=_mock_weather_client(),
    ) as mock_cls:
        resp = await client.get("/api/time-date-weather-location/lookup/51.1000,17.0333")

    assert resp.status_code == 200
    mock_cls.return_value.get.assert_awaited_once()
    call_args = mock_cls.return_value.get.await_args
    assert "@51.1000,17.0333" in call_args.args[0]


@pytest.mark.asyncio
async def test_weather_locations_unauthorized(client: AsyncClient) -> None:
    resp = await client.get("/api/time-date-weather-location/locations")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_weather_config(client: AsyncClient) -> None:
    resp = await client.get("/api/time-date-weather-location/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["label"] == "Wrocław"
    assert data["query"] == "Wroclaw"


@pytest.mark.asyncio
async def test_weather_location_crud(auth_client: AsyncClient) -> None:
    with patch(
        "app.services.weather.httpx.AsyncClient",
        return_value=_mock_weather_client(),
    ):
        create_resp = await auth_client.post(
            "/api/time-date-weather-location/locations",
            json={"label": "London", "query": "London"},
        )
        assert create_resp.status_code == 201
        created = create_resp.json()
        assert created["label"] == "London"
        assert created["query"] == "London"

        list_resp = await auth_client.get("/api/time-date-weather-location/locations")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1

        delete_resp = await auth_client.delete(f"/api/time-date-weather-location/locations/{created['id']}")
        assert delete_resp.status_code == 204

        list_after = await auth_client.get("/api/time-date-weather-location/locations")
        assert list_after.json() == []


@pytest.mark.asyncio
async def test_weather_location_cannot_delete_default(auth_client: AsyncClient) -> None:
    with patch(
        "app.services.weather.httpx.AsyncClient",
        return_value=_mock_weather_client(),
    ):
        create_resp = await auth_client.post(
            "/api/time-date-weather-location/locations",
            json={"label": "Wrocław", "query": "Wroclaw"},
        )
        assert create_resp.status_code == 201
        created = create_resp.json()

        delete_resp = await auth_client.delete(f"/api/time-date-weather-location/locations/{created['id']}")
        assert delete_resp.status_code == 422
        assert "default" in delete_resp.json()["detail"].lower()

        list_resp = await auth_client.get("/api/time-date-weather-location/locations")
        assert len(list_resp.json()) == 1
        assert list_resp.json()[0]["id"] == created["id"]


@pytest.mark.asyncio
async def test_weather_location_duplicate(auth_client: AsyncClient) -> None:
    with patch(
        "app.services.weather.httpx.AsyncClient",
        return_value=_mock_weather_client(),
    ):
        first = await auth_client.post(
            "/api/time-date-weather-location/locations",
            json={"label": "Minsk", "query": "Minsk"},
        )
        assert first.status_code == 201

        second = await auth_client.post(
            "/api/time-date-weather-location/locations",
            json={"label": "Minsk", "query": "Minsk"},
        )
        assert second.status_code == 422
        assert "already" in second.json()["detail"].lower()


@pytest.mark.asyncio
async def test_weather_location_invalid_query(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/time-date-weather-location/locations",
        json={"label": "Bad", "query": "Paris123"},
    )
    assert resp.status_code == 422
    assert "invalid" in resp.json()["detail"].lower()
