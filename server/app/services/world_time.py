"""World Time API client (timeapi.world — worldtimeapi.org compatible)."""

import json
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.logging import logger
from app.core.redis import cache_get, cache_set
from app.settings import get_settings

WORLD_TIME_CACHE_TTL = 60


@dataclass(frozen=True)
class WorldTimePayload:
    timezone: str
    datetime: str
    utc_datetime: str
    utc_offset: str
    unixtime: int
    dst: bool
    abbreviation: str


def _timezone_api_path(iana: str) -> str:
    """Build API path segments from an IANA timezone id."""
    return "/".join(part.strip() for part in iana.split("/") if part.strip())


class WorldTimeService:
    def __init__(self) -> None:
        self._base_url = get_settings().WORLD_TIME_API_BASE.rstrip("/")

    def _timezone_url(self, iana: str) -> str:
        path = _timezone_api_path(iana)
        return f"{self._base_url}/timezone/{path}"

    @staticmethod
    def _parse_payload(data: dict[str, Any]) -> WorldTimePayload | None:
        timezone = data.get("timezone")
        datetime_value = data.get("datetime")
        utc_datetime = data.get("utc_datetime")
        utc_offset = data.get("utc_offset")
        unixtime = data.get("unixtime")
        abbreviation = data.get("abbreviation")
        if not isinstance(timezone, str) or not timezone:
            return None
        if not isinstance(datetime_value, str) or not datetime_value:
            return None
        if not isinstance(utc_datetime, str) or not utc_datetime:
            return None
        if not isinstance(utc_offset, str) or not utc_offset:
            return None
        if not isinstance(unixtime, int | float):
            return None
        if not isinstance(abbreviation, str):
            abbreviation = ""
        return WorldTimePayload(
            timezone=timezone,
            datetime=datetime_value,
            utc_datetime=utc_datetime,
            utc_offset=utc_offset,
            unixtime=int(unixtime),
            dst=bool(data.get("dst")),
            abbreviation=abbreviation,
        )

    async def fetch_timezone_time(self, iana: str) -> WorldTimePayload | None:
        """Fetch current time for an IANA timezone."""
        trimmed = iana.strip()
        if not trimmed or "/" not in trimmed:
            return None

        cache_key = f"world_time:{trimmed}"
        cached = await cache_get(cache_key)
        if cached is not None:
            try:
                data = json.loads(cached)
                if isinstance(data, dict):
                    parsed = self._parse_payload(data)
                    if parsed is not None:
                        return parsed
            except (TypeError, ValueError, json.JSONDecodeError):
                pass

        url = self._timezone_url(trimmed)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=5)
        except httpx.HTTPError as exc:
            logger.warning(
                "World Time API request failed",
                error=exc,
                context={"timezone": trimmed},
            )
            return None

        if resp.status_code != 200:
            logger.warning(
                "World Time API returned error",
                context={"timezone": trimmed, "status": resp.status_code},
            )
            return None

        payload = resp.json()
        if not isinstance(payload, dict):
            return None

        parsed = self._parse_payload(payload)
        if parsed is None:
            return None

        await cache_set(cache_key, json.dumps(payload), ttl=WORLD_TIME_CACHE_TTL)
        return parsed
