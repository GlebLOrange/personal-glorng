"""Weather lookup with Redis caching."""

import json
import re
from typing import Any

import httpx

from app.core.exceptions import ApiError, ValidationError
from app.core.logging import logger
from app.core.redis import cache_get, cache_set, get_redis_client
from app.settings import get_settings

WEATHER_API_URL = "https://wttr.in"
SITE_CITY_KEY = "site:weather:city"
_CITY_PATTERN = re.compile(r"^[a-zA-Z\s\-'.]+$")


class WeatherService:
    async def get_display_city(self) -> str:
        stored = await cache_get(SITE_CITY_KEY)
        if stored:
            return stored
        return get_settings().WEATHER_DEFAULT_CITY

    async def set_display_city(self, city: str) -> str:
        trimmed = city.strip()
        if not trimmed or not _CITY_PATTERN.match(trimmed):
            raise ValidationError("City name contains invalid characters")
        await get_redis_client().set(SITE_CITY_KEY, trimmed)
        logger.info("Display weather city updated", context={"city": trimmed})
        return trimmed

    async def get_display_weather(self) -> dict[str, Any]:
        return await self.get_weather(await self.get_display_city())

    async def get_weather(self, city: str) -> dict[str, Any]:
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
        except httpx.HTTPError as exc:
            logger.error("Weather API error", error=exc, context={"city": normalized})
            raise ApiError(502, f"Weather API unreachable for '{city}'") from None

        if resp.status_code != 200:
            raise ApiError(502, f"Weather API returned {resp.status_code} for '{city}'")

        data: dict[str, Any] = resp.json()
        await cache_set(cache_key, json.dumps(data), ttl=600)
        logger.info("Weather fetched", context={"city": normalized})
        return data
