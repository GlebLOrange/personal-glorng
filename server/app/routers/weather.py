from typing import Any

from fastapi import APIRouter, Depends, Path

from app.core.deps import AppSettings, CurrentUser
from app.core.exceptions import ApiError
from app.core.rate_limit import rate_limit_api
from app.db.deps import DbRegistry
from app.schemas.weather import (
    WeatherLocationCreate,
    WeatherLocationReorder,
    WeatherLocationResponse,
)
from app.schemas.world_time import WorldTimeResponse
from app.services.weather import WeatherService
from app.services.weather_location import WeatherLocationService

router = APIRouter(
    prefix="/time-date-weather-location",
    tags=["time-date-weather-location"],
    dependencies=[Depends(rate_limit_api)],
)


@router.get("/config")
async def get_weather_config(settings: AppSettings) -> dict[str, str]:
    """Public default city config for section seeding and fallbacks."""
    return {
        "label": settings.WEATHER_DEFAULT_LABEL,
        "query": settings.WEATHER_DEFAULT_QUERY,
    }


@router.get(
    "/lookup/{location:path}",
    summary="Lookup weather",
    description="Public weather lookup for a city name or lat,lon coordinate pair.",
)
async def lookup_weather(location: str = Path(max_length=100)) -> dict[str, Any]:
    return await WeatherService().get_weather(location)


def _world_time_from_weather(data: dict[str, Any]) -> WorldTimeResponse:
    zones = data.get("time_zone") or []
    if not zones:
        raise ApiError(502, "Time data unavailable for this location")
    zone = zones[0]
    timezone = zone.get("timezone")
    datetime_value = zone.get("datetime")
    unixtime = zone.get("unixtime")
    if not isinstance(timezone, str) or not isinstance(datetime_value, str):
        raise ApiError(502, "Time data unavailable for this location")
    if not isinstance(unixtime, int | float):
        raise ApiError(502, "Time data unavailable for this location")
    utc_offset = zone.get("utcOffset", "")
    abbreviation = zone.get("abbreviation", "")
    return WorldTimeResponse(
        timezone=timezone,
        datetime=datetime_value,
        utc_datetime=zone.get("utc_datetime", datetime_value),
        utc_offset=str(utc_offset) if utc_offset else "+00:00",
        unixtime=int(unixtime),
        dst=bool(zone.get("dst")),
        abbreviation=str(abbreviation) if abbreviation else "",
    )


@router.get("/time/{location:path}", response_model=WorldTimeResponse)
async def lookup_world_time(location: str = Path(max_length=100)) -> WorldTimeResponse:
    """Public world clock for a city name or lat,lon coordinate pair."""
    data = await WeatherService().get_weather(location)
    return _world_time_from_weather(data)


@router.get("/locations", response_model=list[WeatherLocationResponse])
async def list_weather_locations(
    registry: DbRegistry,
    user: CurrentUser,
) -> list[WeatherLocationResponse]:
    locations = await WeatherLocationService(registry).list_locations(user.id)
    return [WeatherLocationResponse.model_validate(loc) for loc in locations]


@router.post(
    "/locations",
    response_model=WeatherLocationResponse,
    status_code=201,
    summary="Add saved location",
    description="Save a weather location for the authenticated user.",
)
async def add_weather_location(
    body: WeatherLocationCreate,
    registry: DbRegistry,
    user: CurrentUser,
) -> WeatherLocationResponse:
    location = await WeatherLocationService(registry).add_location(
        user.id,
        label=body.label,
        query=body.query,
    )
    return WeatherLocationResponse.model_validate(location)


@router.delete(
    "/locations/{location_id}",
    status_code=204,
    summary="Remove saved location",
    description="Remove a saved weather location.",
)
async def remove_weather_location(
    location_id: int,
    registry: DbRegistry,
    user: CurrentUser,
) -> None:
    await WeatherLocationService(registry).remove_location(user.id, location_id)


@router.put(
    "/locations/reorder",
    response_model=list[WeatherLocationResponse],
    summary="Reorder saved locations",
    description="Reorder saved weather locations.",
)
async def reorder_weather_locations(
    body: WeatherLocationReorder,
    registry: DbRegistry,
    user: CurrentUser,
) -> list[WeatherLocationResponse]:
    locations = await WeatherLocationService(registry).reorder_locations(
        user.id,
        body.ordered_ids,
    )
    return [WeatherLocationResponse.model_validate(loc) for loc in locations]
