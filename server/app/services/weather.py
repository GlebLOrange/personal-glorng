"""Weather lookup with Redis caching."""

import json
import re
from typing import Any

import httpx

from app.core.exceptions import ApiError, ValidationError
from app.core.logging import logger
from app.core.redis import cache_get, cache_set

WEATHER_API_URL = "https://wttr.in"
_CITY_PATTERN = re.compile(r"^[a-zA-Z\s\-'.]+$")
_COORD_PATTERN = re.compile(r"^-?\d{1,3}(\.\d+)?,-?\d{1,3}(\.\d+)?$")


def is_valid_location(location: str) -> bool:
    """Return True when location is a valid city name or lat,lon pair."""
    trimmed = location.strip()
    if not trimmed:
        return False
    return bool(_CITY_PATTERN.match(trimmed) or _COORD_PATTERN.match(trimmed))


def normalize_location(location: str) -> str:
    """Normalize location for cache keys and wttr.in requests."""
    trimmed = location.strip()
    if _COORD_PATTERN.match(trimmed):
        return trimmed
    return trimmed.lower()


def wttr_path(location: str) -> str:
    """Build wttr.in path segment for a city or coordinate pair."""
    trimmed = location.strip()
    if _COORD_PATTERN.match(trimmed):
        return f"@{trimmed}"
    return normalize_location(trimmed)


class WeatherService:
    async def get_weather(self, location: str) -> dict[str, Any]:
        trimmed = location.strip()
        if not is_valid_location(trimmed):
            raise ValidationError("Location contains invalid characters")

        normalized = normalize_location(trimmed)
        cache_key = f"weather:{normalized}"
        cached = await cache_get(cache_key)
        if cached:
            logger.debug("Weather cache hit", context={"location": normalized})
            return json.loads(cached)

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{WEATHER_API_URL}/{wttr_path(trimmed)}",
                    params={"format": "j1"},
                    timeout=10,
                )
        except httpx.TimeoutException:
            logger.warning("Weather API timeout", context={"location": normalized})
            raise ApiError(504, f"Weather API timed out for '{trimmed}'") from None
        except httpx.HTTPError as exc:
            logger.error(
                "Weather API error",
                error=exc,
                context={"location": normalized},
            )
            raise ApiError(502, f"Weather API unreachable for '{trimmed}'") from None

        if resp.status_code != 200:
            raise ApiError(
                502,
                f"Weather API returned {resp.status_code} for '{trimmed}'",
            )

        data: dict[str, Any] = resp.json()
        await cache_set(cache_key, json.dumps(data), ttl=600)
        logger.info("Weather fetched", context={"location": normalized})
        return data
