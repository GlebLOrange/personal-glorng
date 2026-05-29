from typing import Any

from fastapi import APIRouter, Depends, Path

from app.core.deps import require_capability
from app.services.weather import WeatherService

router = APIRouter(
    prefix="/weather",
    dependencies=[Depends(require_capability("weather", "read"))],
)


@router.get("/{city}")
async def get_weather(city: str = Path(max_length=100)) -> dict[str, Any]:
    return await WeatherService().get_weather(city)
