"""Date range helpers shared by API filters and services."""

from calendar import monthrange
from datetime import date, datetime

from app.core.exceptions import ValidationError


def month_date_bounds(month: str) -> tuple[date, date]:
    """Return inclusive calendar bounds for a YYYY-MM month value."""
    parts = month.split("-", 1)
    if len(parts) != 2:
        raise ValidationError("month must be YYYY-MM")
    try:
        year, mon = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise ValidationError("month must be YYYY-MM") from exc
    if not 1 <= mon <= 12:
        raise ValidationError("month must be YYYY-MM")
    last_day = monthrange(year, mon)[1]
    return date(year, mon, 1), date(year, mon, last_day)


def date_range_bounds(
    date_from: date | None,
    date_to: date | None,
) -> dict[str, datetime] | None:
    """Build inclusive occurred_at Mongo bounds from calendar dates."""
    if not date_from and not date_to:
        return None
    occurred: dict[str, datetime] = {}
    if date_from:
        occurred["$gte"] = datetime.combine(date_from, datetime.min.time())
    if date_to:
        occurred["$lte"] = datetime.combine(date_to, datetime.max.time())
    return occurred
