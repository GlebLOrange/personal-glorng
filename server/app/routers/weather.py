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


@router.get("/config")
async def get_weather_config() -> dict[str, str]:
    """Public default city config for section seeding and fallbacks."""
    settings = get_settings()
    return {
        "label": settings.WEATHER_DEFAULT_LABEL,
        "query": settings.WEATHER_DEFAULT_QUERY,
    }


@router.get("/lookup/{location:path}")
async def lookup_weather(location: str = Path(max_length=100)) -> dict[str, Any]:
    """Public weather lookup for a city name or lat,lon coordinate pair."""
    return await WeatherService().get_weather(location)


@router.get("/locations", response_model=list[WeatherLocationResponse])
async def list_weather_locations(
    db: DbSession,
    user: CurrentUser,
) -> list[WeatherLocationResponse]:
    """List saved locations for the authenticated user."""
    locations = await WeatherLocationService().list_locations(db, user.id)
    return [WeatherLocationResponse.model_validate(loc) for loc in locations]


@router.post("/locations", response_model=WeatherLocationResponse, status_code=201)
async def add_weather_location(
    body: WeatherLocationCreate,
    db: DbSession,
    user: CurrentUser,
) -> WeatherLocationResponse:
    """Save a weather location for the authenticated user."""
    location = await WeatherLocationService().add_location(
        db,
        user.id,
        label=body.label,
        query=body.query,
    )
    return WeatherLocationResponse.model_validate(location)


@router.delete("/locations/{location_id}", status_code=204)
async def remove_weather_location(
    location_id: int,
    db: DbSession,
    user: CurrentUser,
) -> None:
    """Remove a saved weather location."""
    await WeatherLocationService().remove_location(db, user.id, location_id)


@router.put("/locations/reorder", response_model=list[WeatherLocationResponse])
async def reorder_weather_locations(
    body: WeatherLocationReorder,
    db: DbSession,
    user: CurrentUser,
) -> list[WeatherLocationResponse]:
    """Reorder saved weather locations."""
    locations = await WeatherLocationService().reorder_locations(
        db,
        user.id,
        body.ordered_ids,
    )
    return [WeatherLocationResponse.model_validate(loc) for loc in locations]
