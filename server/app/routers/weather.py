from typing import Any

from fastapi import APIRouter, Depends

from app.core.rate_limit import rate_limit_api
from app.schemas.weather import WeatherConfigResponse
from app.services.weather import WeatherService

router = APIRouter(
    prefix="/weather",
    tags=["weather"],
    dependencies=[Depends(rate_limit_api)],
)


@router.get("/config", response_model=WeatherConfigResponse)
async def get_weather_config() -> WeatherConfigResponse:
    """Public site display city."""
    city = await WeatherService().get_display_city()
    return WeatherConfigResponse(city=city)


@router.get("/current")
async def get_current_weather() -> dict[str, Any]:
    """Public weather for the site display city."""
    return await WeatherService().get_display_weather()
