"""Local timezone clock payloads (IANA via zoneinfo).

Replaces the old World Time HTTP API (timeapi.world / worldtimeapi.org), which
now redirects to RapidAPI and requires a key.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class WorldTimePayload:
    timezone: str
    datetime: str
    utc_datetime: str
    utc_offset: str
    unixtime: int
    dst: bool
    abbreviation: str


def _format_utc_offset(total_seconds: int) -> str:
    """Format an offset as +/-HH:MM (World Time API compatible)."""
    sign = "+" if total_seconds >= 0 else "-"
    abs_seconds = abs(total_seconds)
    hours, rem = divmod(abs_seconds, 3600)
    minutes = rem // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


class WorldTimeService:
    """Build current-time payloads from the system timezone database."""

    async def fetch_timezone_time(self, iana: str) -> WorldTimePayload | None:
        """Return current time for an IANA timezone, or None if unknown."""
        trimmed = iana.strip()
        if not trimmed or "/" not in trimmed:
            return None
        try:
            tz = ZoneInfo(trimmed)
        except ZoneInfoNotFoundError:
            return None

        now = datetime.now(tz)
        offset = now.utcoffset()
        if offset is None:
            return None

        utc_now = now.astimezone(UTC)
        dst = now.dst()
        return WorldTimePayload(
            timezone=trimmed,
            datetime=now.isoformat(),
            utc_datetime=utc_now.isoformat(),
            utc_offset=_format_utc_offset(int(offset.total_seconds())),
            unixtime=int(now.timestamp()),
            dst=bool(dst and dst.total_seconds()),
            abbreviation=now.tzname() or "",
        )
