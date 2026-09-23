"""Documents for website/API health monitors and check history."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.db.documents.base import TimestampedDocument


class DnsRecord(BaseModel):
    """One resolved DNS address for a monitored host."""

    family: str
    address: str


class HealthMonitor(TimestampedDocument):
    """User-owned URL monitor with cached latest probe snapshot."""

    url: str
    label: str | None = None
    interval_minutes: int = 5
    enabled: bool = True
    created_by: int
    next_check_at: datetime | None = None
    last_checked_at: datetime | None = None
    last_status_code: int | None = None
    last_response_ms: float | None = None
    last_ok: bool | None = None
    last_error: str | None = None
    uptime_percent: float | None = None
    ssl_expires_at: datetime | None = None
    dns: list[DnsRecord] = Field(default_factory=list)


class HealthCheckResult(TimestampedDocument):
    """Single probe result for historical charts and uptime."""

    monitor_id: int
    checked_at: datetime
    status_code: int | None = None
    response_ms: float | None = None
    ok: bool = False
    error: str | None = None
    ssl_expires_at: datetime | None = None
