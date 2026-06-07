from typing import Any

from fastapi import APIRouter, Depends, Path

from app.core.deps import CurrentUser, DbSession
from app.core.rate_limit import rate_limit_api
from app.schemas.weather import (
    WeatherLocationCreate,
    WeatherLocationReorder,
    WeatherLocationResponse,
)
from app.services.weather import WeatherService
from app.services.weather_location import WeatherLocationService
from app.settings import get_settings

router = APIRouter(
    prefix="/time-date-weather-location",
    tags=["time-date-weather-location"],
    dependencies=[Depends(rate_limit_api)],
)


@router.get(
    "/config",
    summary="Get weather config",
    description="Public default city config for section seeding and fallbacks.",
)
async def get_weather_config() -> dict[str, str]:
    settings = get_settings()
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


@router.get(
    "/locations",
    response_model=list[WeatherLocationResponse],
    summary="List saved locations",
    description="List saved weather locations for the authenticated user.",
)
async def list_weather_locations(
    db: DbSession,
    user: CurrentUser,
) -> list[WeatherLocationResponse]:
    locations = await WeatherLocationService().list_locations(db, user.id)
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
    db: DbSession,
    user: CurrentUser,
) -> WeatherLocationResponse:
    location = await WeatherLocationService().add_location(
        db,
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
    db: DbSession,
    user: CurrentUser,
) -> None:
    await WeatherLocationService().remove_location(db, user.id, location_id)


@router.put(
    "/locations/reorder",
    response_model=list[WeatherLocationResponse],
    summary="Reorder saved locations",
    description="Reorder saved weather locations.",
)
async def reorder_weather_locations(
    body: WeatherLocationReorder,
    db: DbSession,
    user: CurrentUser,
) -> list[WeatherLocationResponse]:
    locations = await WeatherLocationService().reorder_locations(
        db,
        user.id,
        body.ordered_ids,
    )
    return [WeatherLocationResponse.model_validate(loc) for loc in locations]
