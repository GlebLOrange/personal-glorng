from typing import Any

from fastapi import APIRouter, Depends, Path

from app.core.deps import require_capability
from app.schemas.weather import WeatherCityUpdate, WeatherConfigResponse
from app.services.weather import WeatherService

router = APIRouter(prefix="/weather")


@router.put(
    "/city",
    response_model=WeatherConfigResponse,
    dependencies=[Depends(require_capability("weather", "write"))],
)
async def set_display_city(body: WeatherCityUpdate) -> WeatherConfigResponse:
    """Set the site-wide display city."""
    city = await WeatherService().set_display_city(body.city)
    return WeatherConfigResponse(city=city)


@router.get(
    "/{city}",
    dependencies=[Depends(require_capability("weather", "read"))],
)
async def get_weather(city: str = Path(max_length=100)) -> dict[str, Any]:
    return await WeatherService().get_weather(city)
