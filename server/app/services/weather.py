"""Weather lookup with Redis caching."""

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.cache_json import safe_cache_json_loads
from app.core.exceptions import ApiError, ValidationError
from app.core.logging import logger
from app.core.redis import cache_get, cache_set
from app.services.world_time import WorldTimePayload, WorldTimeService

WEATHER_API_URL = "https://wttr.in"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TZ_INFO_CACHE_TTL = 86_400
_CITY_PATTERN = re.compile(r"^[a-zA-Z\s\-'.]+$")
_COORD_PATTERN = re.compile(r"^-?\d{1,3}(\.\d+)?,-?\d{1,3}(\.\d+)?$")


@dataclass(frozen=True)
class TimezoneInfo:
    iana: str
    offset_hours: float


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
    except KeyError, TypeError, ValueError:
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return lat, lon


def _format_utc_offset(hours: float) -> str:
    """Format UTC offset the way wttr.in used to expose it."""
    if hours >= 0:
        return f"+{hours:.1f}"
    return f"{hours:.1f}"


def _parse_utc_offset_hours(value: str) -> float | None:
    """Parse wttr-style or World Time API UTC offset strings to hours."""
    if ":" in value:
        sign = 1
        cleaned = value
        if cleaned.startswith("-"):
            sign = -1
            cleaned = cleaned[1:]
        elif cleaned.startswith("+"):
            cleaned = cleaned[1:]
        parts = cleaned.split(":", 1)
        try:
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            return sign * (hours + minutes / 60)
        except ValueError:
            return None
    try:
        return float(value)
    except ValueError:
        return None


def _utc_offset_hours_from_world_time(payload: WorldTimePayload) -> float | None:
    return _parse_utc_offset_hours(payload.utc_offset)


def _world_time_zone_entry(payload: WorldTimePayload) -> dict[str, Any]:
    offset_hours = _utc_offset_hours_from_world_time(payload)
    utc_offset = (
        _format_utc_offset(offset_hours)
        if offset_hours is not None
        else payload.utc_offset
    )
    return {
        "utcOffset": utc_offset,
        "timezone": payload.timezone,
        "datetime": payload.datetime,
        "utc_datetime": payload.utc_datetime,
        "unixtime": payload.unixtime,
        "dst": payload.dst,
        "abbreviation": payload.abbreviation,
    }


def _needs_time_enrichment(data: dict[str, Any]) -> bool:
    zones = data.get("time_zone") or []
    if not zones:
        return True
    return zones[0].get("unixtime") is None


async def _resolve_timezone_info(lat: float, lon: float) -> TimezoneInfo | None:
    """Resolve IANA timezone and UTC offset for coordinates via Open-Meteo."""
    cache_key = f"tz_info:{lat:.2f},{lon:.2f}"
    cached = await cache_get(cache_key)
    if cached is not None:
        try:
            payload = json.loads(cached)
            if isinstance(payload, dict):
                iana = payload.get("iana")
                offset_hours = payload.get("offset_hours")
                if isinstance(iana, str) and isinstance(offset_hours, int | float):
                    return TimezoneInfo(iana=iana, offset_hours=float(offset_hours))
        except TypeError, ValueError, json.JSONDecodeError:
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
    iana = payload.get("timezone")
    offset_seconds = payload.get("utc_offset_seconds")
    if not isinstance(iana, str) or not iana or "/" not in iana:
        return None
    if not isinstance(offset_seconds, int | float):
        return None

    info = TimezoneInfo(iana=iana, offset_hours=float(offset_seconds) / 3600)
    await cache_set(
        cache_key,
        json.dumps({"iana": info.iana, "offset_hours": info.offset_hours}),
        ttl=TZ_INFO_CACHE_TTL,
    )
    return info


async def _resolve_utc_offset_hours(lat: float, lon: float) -> float | None:
    """Backward-compatible offset resolver for tests and fallbacks."""
    info = await _resolve_timezone_info(lat, lon)
    return info.offset_hours if info else None


async def enrich_weather_timezone(data: dict[str, Any]) -> dict[str, Any]:
    """Backfill timezone metadata and World Time API clock data."""
    if not _needs_time_enrichment(data):
        return data

    coords = _extract_coordinates(data)
    if coords is None:
        return data

    tz_info = await _resolve_timezone_info(*coords)
    if tz_info is None:
        return data

    world_time = await WorldTimeService().fetch_timezone_time(tz_info.iana)
    if world_time is not None:
        data["time_zone"] = [_world_time_zone_entry(world_time)]
        return data

    zones = data.get("time_zone") or []
    if zones and zones[0].get("utcOffset"):
        return data

    data["time_zone"] = [{"utcOffset": _format_utc_offset(tz_info.offset_hours)}]
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
            data = safe_cache_json_loads(cached)
            if isinstance(data, dict):
                if _needs_time_enrichment(data):
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
