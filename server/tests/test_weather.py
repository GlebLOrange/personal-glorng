from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.services.weather import TimezoneInfo, enrich_weather_timezone
from app.services.world_time import WorldTimePayload
from tests.factories import create_user

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
async def test_weather_location_mutations_unauthorized(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/time-date-weather-location/locations",
        json={"label": "London", "query": "London"},
    )
    assert create_resp.status_code == 401

    delete_resp = await client.delete("/api/time-date-weather-location/locations/1")
    assert delete_resp.status_code == 401

    reorder_resp = await client.put(
        "/api/time-date-weather-location/locations/reorder",
        json={"ordered_ids": [1]},
    )
    assert reorder_resp.status_code == 401


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


@pytest.mark.asyncio
async def test_weather_location_delete_other_user_forbidden(
    client: AsyncClient,
    db: AsyncSession,
) -> None:
    owner = await create_user(db, email="owner@example.com", password="pass12345")
    other = await create_user(db, email="other@example.com", password="pass12345")
    await db.commit()

    owner_token = create_access_token(str(owner.public_id))
    other_token = create_access_token(str(other.public_id))

    with patch(
        "app.services.weather.httpx.AsyncClient",
        return_value=_mock_weather_client(),
    ):
        create_resp = await client.post(
            "/api/time-date-weather-location/locations",
            json={"label": "London", "query": "London"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert create_resp.status_code == 201
        location_id = create_resp.json()["id"]

        delete_resp = await client.delete(
            f"/api/time-date-weather-location/locations/{location_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert delete_resp.status_code == 404


@pytest.mark.asyncio
async def test_enrich_weather_timezone_adds_world_time_fields() -> None:
    payload = {
        "nearest_area": [{"latitude": "51.100", "longitude": "17.033"}],
        "current_condition": [{"temp_C": "16"}],
    }
    world_time = WorldTimePayload(
        timezone="Europe/Warsaw",
        datetime="2026-06-07T14:00:00+02:00",
        utc_datetime="2026-06-07T12:00:00+00:00",
        utc_offset="+02:00",
        unixtime=1_780_833_600,
        dst=True,
        abbreviation="CEST",
    )
    with (
        patch(
            "app.services.weather._resolve_timezone_info",
            new=AsyncMock(
                return_value=TimezoneInfo(iana="Europe/Warsaw", offset_hours=2.0),
            ),
        ),
        patch(
            "app.services.weather.WorldTimeService.fetch_timezone_time",
            new=AsyncMock(return_value=world_time),
        ),
    ):
        result = await enrich_weather_timezone(payload)

    zone = result["time_zone"][0]
    assert zone["utcOffset"] == "+2.0"
    assert zone["timezone"] == "Europe/Warsaw"
    assert zone["unixtime"] == 1_780_833_600


@pytest.mark.asyncio
async def test_enrich_weather_timezone_fallback_when_world_time_fails() -> None:
    payload = {
        "nearest_area": [{"latitude": "51.100", "longitude": "17.033"}],
        "current_condition": [{"temp_C": "16"}],
    }
    with (
        patch(
            "app.services.weather._resolve_timezone_info",
            new=AsyncMock(
                return_value=TimezoneInfo(iana="Europe/Warsaw", offset_hours=2.0),
            ),
        ),
        patch(
            "app.services.weather.WorldTimeService.fetch_timezone_time",
            new=AsyncMock(return_value=None),
        ),
    ):
        result = await enrich_weather_timezone(payload)

    assert result["time_zone"] == [{"utcOffset": "+2.0"}]


@pytest.mark.asyncio
async def test_enrich_weather_timezone_skips_when_unixtime_present() -> None:
    payload = {
        "time_zone": [{"utcOffset": "+1.0", "unixtime": 1_749_300_000}],
        "nearest_area": [{"latitude": "51.100", "longitude": "17.033"}],
    }
    with patch(
        "app.services.weather._resolve_timezone_info",
        new=AsyncMock(
            return_value=TimezoneInfo(iana="Europe/Warsaw", offset_hours=9.0),
        ),
    ) as mock_resolve:
        result = await enrich_weather_timezone(payload)

    assert result["time_zone"][0]["unixtime"] == 1_749_300_000
    mock_resolve.assert_not_awaited()
