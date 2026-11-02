"""Tests for local World Time payloads."""

from datetime import datetime
from unittest.mock import AsyncMock
from zoneinfo import ZoneInfo

import pytest
from httpx import AsyncClient

from app.core.deps import get_weather_service
from app.main import app
from app.services.world_time import WorldTimePayload, WorldTimeService


@pytest.mark.asyncio
async def test_fetch_timezone_time_from_zoneinfo() -> None:
    """IANA zones resolve to a full clock payload without an HTTP call."""
    result = await WorldTimeService().fetch_timezone_time("Europe/Warsaw")

    assert isinstance(result, WorldTimePayload)
    assert result.timezone == "Europe/Warsaw"
    assert result.utc_offset.startswith(("+", "-"))
    assert ":" in result.utc_offset
    assert result.unixtime > 0
    assert result.datetime
    assert result.utc_datetime
    # Matches wall clock for that zone within a second of "now".
    expected = int(datetime.now(ZoneInfo("Europe/Warsaw")).timestamp())
    assert abs(result.unixtime - expected) <= 1


@pytest.mark.asyncio
async def test_fetch_timezone_time_rejects_unknown_zone() -> None:
    """Unknown IANA ids return None."""
    assert await WorldTimeService().fetch_timezone_time("Not/ARealZone") is None
    assert await WorldTimeService().fetch_timezone_time("UTC") is None


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
                "unixtime": 1_799_999_900,
                "dst": True,
                "abbreviation": "BST",
            }
        ],
    }

    async def fake_weather_service():
        return AsyncMock(get_weather=AsyncMock(return_value=enriched_weather))

    app.dependency_overrides[get_weather_service] = fake_weather_service
    try:
        resp = await client.get("/api/weather/time/London")
    finally:
        app.dependency_overrides.pop(get_weather_service, None)

    assert resp.status_code == 200
    data = resp.json()
    assert data["timezone"] == "Europe/London"
    assert data["unixtime"] == 1_799_999_900
