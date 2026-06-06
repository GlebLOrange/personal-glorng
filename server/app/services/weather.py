"""Weather lookup with Redis caching."""

import json
import re
from typing import Any

import httpx

from app.core.exceptions import ApiError, ValidationError
from app.core.logging import logger
from app.core.redis import cache_get, cache_set

WEATHER_API_URL = "https://wttr.in"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TZ_OFFSET_CACHE_TTL = 86_400
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


def _extract_coordinates(data: dict[str, Any]) -> tuple[float, float] | None:
    """Read lat/lon from a wttr.in nearest_area block."""
    areas = data.get("nearest_area") or []
    if not areas:
        return None
    area = areas[0]
    try:
        lat = float(area["latitude"])
        lon = float(area["longitude"])
    except (KeyError, TypeError, ValueError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return lat, lon


def _format_utc_offset(hours: float) -> str:
    """Format UTC offset the way wttr.in used to expose it."""
    if hours >= 0:
        return f"+{hours:.1f}"
    return f"{hours:.1f}"


def _has_utc_offset(data: dict[str, Any]) -> bool:
    zones = data.get("time_zone") or []
    return bool(zones and zones[0].get("utcOffset"))


async def _resolve_utc_offset_hours(lat: float, lon: float) -> float | None:
    """Resolve DST-aware UTC offset for coordinates via Open-Meteo."""
    cache_key = f"tz_offset:{lat:.2f},{lon:.2f}"
    cached = await cache_get(cache_key)
    if cached is not None:
        try:
            return float(cached)
        except ValueError:
            pass

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                OPEN_METEO_FORECAST_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m",
                    "timezone": "auto",
                },
                timeout=5,
            )
    except httpx.HTTPError as exc:
        logger.warning(
            "Timezone lookup failed",
            error=exc,
            context={"lat": lat, "lon": lon},
        )
        return None

    if resp.status_code != 200:
        return None

    payload = resp.json()
    offset_seconds = payload.get("utc_offset_seconds")
    if not isinstance(offset_seconds, int | float):
        return None

    hours = offset_seconds / 3600
    await cache_set(cache_key, str(hours), ttl=TZ_OFFSET_CACHE_TTL)
    return hours


async def enrich_weather_timezone(data: dict[str, Any]) -> dict[str, Any]:
    """Backfill utcOffset when wttr.in omits time_zone from j1 payloads."""
    if _has_utc_offset(data):
        return data

    coords = _extract_coordinates(data)
    if coords is None:
        return data

    offset_hours = await _resolve_utc_offset_hours(*coords)
    if offset_hours is None:
        return data

    data["time_zone"] = [{"utcOffset": _format_utc_offset(offset_hours)}]
    return data


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
            data: dict[str, Any] = json.loads(cached)
            if not _has_utc_offset(data):
                data = await enrich_weather_timezone(data)
                await cache_set(cache_key, json.dumps(data), ttl=600)
            return data

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

        data = resp.json()
        data = await enrich_weather_timezone(data)
        await cache_set(cache_key, json.dumps(data), ttl=600)
        logger.info("Weather fetched", context={"location": normalized})
        return data
