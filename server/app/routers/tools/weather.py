import json
import re
from typing import Any

import httpx
from fastapi import APIRouter, Depends, Path

from app.core.deps import require_admin
from app.core.exceptions import ApiError, ValidationError
from app.core.logging import logger
from app.core.redis import cache_get, cache_set

router = APIRouter(prefix="/weather", dependencies=[Depends(require_admin)])

WEATHER_API_URL = "https://wttr.in"
_CITY_PATTERN = re.compile(r"^[a-zA-Z\s\-'.]+$")


@router.get("/{city}")
async def get_weather(city: str = Path(max_length=100)) -> dict[str, Any]:
    if not _CITY_PATTERN.match(city):
        raise ValidationError("City name contains invalid characters")

    normalized = city.strip().lower()
    cache_key = f"weather:{normalized}"
    cached = await cache_get(cache_key)
    if cached:
        logger.debug("Weather cache hit", context={"city": normalized})
        return json.loads(cached)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{WEATHER_API_URL}/{normalized}",
                params={"format": "j1"},
                timeout=10,
            )
    except httpx.TimeoutException:
        logger.warning("Weather API timeout", context={"city": normalized})
        raise ApiError(504, f"Weather API timed out for '{city}'") from None
    except httpx.HTTPError as e:
        logger.error("Weather API error", error=e, context={"city": normalized})
        raise ApiError(502, f"Weather API unreachable for '{city}'") from None

    if resp.status_code != 200:
        raise ApiError(502, f"Weather API returned {resp.status_code} for '{city}'")

    data: dict[str, Any] = resp.json()
    await cache_set(cache_key, json.dumps(data), ttl=600)

    logger.info("Weather fetched", context={"city": normalized})
    return data
