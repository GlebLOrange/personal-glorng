"""Date range helpers shared by API filters and services."""

from calendar import monthrange
from datetime import date

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
