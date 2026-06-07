from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.services.world_time import WorldTimePayload, WorldTimeService

WORLD_TIME_API_JSON = {
    "timezone": "Europe/Warsaw",
    "datetime": "2026-06-07T14:00:00+02:00",
    "utc_datetime": "2026-06-07T12:00:00+00:00",
    "utc_offset": "+02:00",
    "unixtime": 1_780_833_600,
    "dst": True,
    "abbreviation": "CEST",
}


def _mock_world_time_client(payload: dict | None = None) -> MagicMock:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = payload or WORLD_TIME_API_JSON

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


@pytest.mark.asyncio
async def test_fetch_timezone_time_parses_response() -> None:
    with (
        patch("app.services.world_time.cache_get", new=AsyncMock(return_value=None)),
        patch("app.services.world_time.cache_set", new=AsyncMock()),
        patch(
            "app.services.world_time.httpx.AsyncClient",
            return_value=_mock_world_time_client(),
        ),
    ):
        result = await WorldTimeService().fetch_timezone_time("Europe/Warsaw")

    assert isinstance(result, WorldTimePayload)
    assert result.timezone == "Europe/Warsaw"
    assert result.unixtime == 1_780_833_600


@pytest.mark.asyncio
async def test_lookup_world_time_endpoint(client: AsyncClient) -> None:
    enriched_weather = {
        "current_condition": [{"temp_C": "20"}],
        "nearest_area": [{"areaName": [{"value": "London"}]}],
        "time_zone": [
            {
                "utcOffset": "+1.0",
                "timezone": "Europe/London",
                "datetime": "2026-06-07T13:00:00+01:00",
                "utc_datetime": "2026-06-07T12:00:00+00:00",
                "unixtime": 1_749_300_000,
                "dst": True,
                "abbreviation": "BST",
            }
        ],
    }
    with patch(
        "app.routers.weather.WeatherService.get_weather",
        new=AsyncMock(return_value=enriched_weather),
    ):
        resp = await client.get("/api/time-date-weather-location/time/London")

    assert resp.status_code == 200
    data = resp.json()
    assert data["timezone"] == "Europe/London"
    assert data["unixtime"] == 1_749_300_000
