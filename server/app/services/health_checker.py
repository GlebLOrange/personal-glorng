"""Website/API health monitor service: probe, persist, schedule."""

from __future__ import annotations

import asyncio
import socket
import ssl
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

import httpx

from app.core.exceptions import ConflictError, ForbiddenError, ValidationError
from app.core.pagination import build_paginated
from app.core.url_safety import get_public_http_url, is_public_http_url
from app.core.utils import DEFAULT_PER_PAGE, paginate_params
from app.db.documents.base import utc_now
from app.db.documents.health_checker import DnsRecord, HealthCheckResult, HealthMonitor
from app.db.registry import DatabaseRegistry
from app.schemas.health_checker import (
    HealthHistoryPoint,
    HealthHistoryResponse,
    HealthMonitorListResponse,
    HealthMonitorResponse,
)
from app.services.audit import AuditService

ALLOWED_INTERVALS = frozenset({1, 5, 15, 60})
MAX_MONITORS_PER_USER = 10
PROBE_TIMEOUT_SECONDS = 10.0
MAX_CHECKS_PER_TICK = 50
HISTORY_HOURS = 24
HISTORY_MAX_POINTS = 288
CLEANUP_RETENTION_DAYS = 30


@dataclass
class ProbeOutcome:
    """Result of a single HTTP/SSL/DNS probe."""

    status_code: int | None = None
    response_ms: float | None = None
    ok: bool = False
    error: str | None = None
    ssl_expires_at: datetime | None = None
    dns: list[DnsRecord] = field(default_factory=list)


def compute_uptime_percent(ok_count: int, total: int) -> float | None:
    """Return rolling uptime percentage, or None when no samples."""
    if total <= 0:
        return None
    return round(100.0 * ok_count / total, 2)


def _hostname(url: str) -> str | None:
    host = urlparse(url).hostname
    if not host:
        return None
    return host.lower().rstrip(".")


def _resolve_dns(hostname: str) -> list[DnsRecord]:
    """Resolve A/AAAA records via getaddrinfo (blocking)."""
    records: list[DnsRecord] = []
    seen: set[tuple[str, str]] = set()
    try:
        results = socket.getaddrinfo(hostname, None)
    except OSError:
        return records
    for family, _type, _proto, _canon, sockaddr in results:
        if not sockaddr:
            continue
        address = str(sockaddr[0])
        if family == socket.AF_INET:
            label = "A"
        elif family == socket.AF_INET6:
            label = "AAAA"
        else:
            continue
        key = (label, address)
        if key in seen:
            continue
        seen.add(key)
        records.append(DnsRecord(family=label, address=address))
    return records


def _ssl_expiry(hostname: str, port: int = 443) -> datetime | None:
    """Return certificate notAfter in UTC, or None on failure."""
    context = ssl.create_default_context()
    try:
        with (
            socket.create_connection((hostname, port), timeout=PROBE_TIMEOUT_SECONDS) as sock,
            context.wrap_socket(sock, server_hostname=hostname) as ssock,
        ):
            cert = ssock.getpeercert()
    except OSError:
        return None
    if not cert:
        return None
    not_after = cert.get("notAfter")
    if not isinstance(not_after, str):
        return None
    try:
        # OpenSSL format: 'Sep 23 12:00:00 2027 GMT'
        naive = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
    except ValueError:
        return None
    return naive.replace(tzinfo=UTC)


async def probe_url(url: str) -> ProbeOutcome:
    """Probe URL for HTTP status/latency, SSL expiry, and DNS."""
    if not is_public_http_url(url):
        return ProbeOutcome(error="URL is not allowed for server-side fetch")

    hostname = _hostname(url)
    dns: list[DnsRecord] = []
    ssl_expires_at: datetime | None = None
    if hostname:
        dns = await asyncio.to_thread(_resolve_dns, hostname)
        if urlparse(url).scheme == "https":
            ssl_expires_at = await asyncio.to_thread(_ssl_expiry, hostname)

    status_code: int | None = None
    response_ms: float | None = None
    error: str | None = None
    ok = False
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=PROBE_TIMEOUT_SECONDS) as client:
            response = await get_public_http_url(client, url)
            status_code = response.status_code
            response_ms = round((time.perf_counter() - started) * 1000, 2)
            await response.aclose()
            ok = 200 <= status_code < 400
            if not ok:
                error = f"HTTP {status_code}"
    except ValueError as exc:
        response_ms = round((time.perf_counter() - started) * 1000, 2)
        error = str(exc)
    except httpx.HTTPError as exc:
        response_ms = round((time.perf_counter() - started) * 1000, 2)
        error = str(exc) or exc.__class__.__name__

    return ProbeOutcome(
        status_code=status_code,
        response_ms=response_ms,
        ok=ok,
        error=error,
        ssl_expires_at=ssl_expires_at,
        dns=dns,
    )


class HealthMonitorService:
    """CRUD and probing for user-owned health monitors."""

    def __init__(self, registry: DatabaseRegistry) -> None:
        self.registry = registry

    def _monitors(self):
        if self.registry.health_monitors is None:
            msg = "Health monitor repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.health_monitors

    def _results(self):
        if self.registry.health_check_results is None:
            msg = "Health check result repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.health_check_results

    def _require_owner(
        self,
        monitor: HealthMonitor,
        actor_id: int,
        *,
        is_superuser: bool = False,
    ) -> None:
        if is_superuser:
            return
        if monitor.created_by != actor_id:
            raise ForbiddenError("You do not have permission to access this monitor")

    async def _get_owned(
        self,
        monitor_id: int,
        actor_id: int,
        *,
        is_superuser: bool = False,
    ) -> HealthMonitor:
        monitor = await self._monitors().get(monitor_id)
        self._require_owner(monitor, actor_id, is_superuser=is_superuser)
        return monitor

    async def list_by_owner(
        self,
        created_by: int,
        *,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> HealthMonitorListResponse:
        offset, limit = paginate_params(page, per_page)
        monitors = await self._monitors().list(
            offset=offset,
            limit=limit,
            created_by=created_by,
            sort=[("created_at", -1)],
        )
        total = await self._monitors().count(created_by=created_by)
        items = [HealthMonitorResponse.model_validate(m) for m in monitors]
        return build_paginated(
            items,
            total=total,
            page=max(1, page),
            per_page=limit,
        )

    async def get_monitor(
        self,
        monitor_id: int,
        actor_id: int,
        *,
        is_superuser: bool = False,
    ) -> HealthMonitor:
        return await self._get_owned(
            monitor_id, actor_id, is_superuser=is_superuser
        )

    async def create_monitor(
        self,
        *,
        url: str,
        created_by: int,
        label: str | None = None,
        interval_minutes: int = 5,
    ) -> HealthMonitor:
        if interval_minutes not in ALLOWED_INTERVALS:
            raise ValidationError("interval_minutes must be 1, 5, 15, or 60")
        if not is_public_http_url(url):
            raise ValidationError("URL is not allowed for monitoring")

        count = await self._monitors().count(created_by=created_by)
        if count >= MAX_MONITORS_PER_USER:
            raise ConflictError(
                f"Maximum of {MAX_MONITORS_PER_USER} monitors per user"
            )

        now = utc_now()
        monitor = HealthMonitor(
            url=url,
            label=label,
            interval_minutes=interval_minutes,
            enabled=True,
            created_by=created_by,
            next_check_at=now,
        )
        monitor = await self._monitors().insert(monitor)
        monitor = await self.run_check(monitor.id)
        await AuditService(self.registry).record_domain(
            action="health_monitor.created",
            resource_type="health_monitor",
            resource_id=monitor.id,
            actor_id=created_by,
            metadata={"url": monitor.url},
        )
        return monitor

    async def update_monitor(
        self,
        monitor_id: int,
        *,
        actor_id: int,
        is_superuser: bool = False,
        fields: dict[str, object] | None = None,
    ) -> HealthMonitor:
        monitor = await self._get_owned(
            monitor_id, actor_id, is_superuser=is_superuser
        )
        payload = dict(fields or {})
        updates: dict[str, object] = {}
        if "label" in payload:
            updates["label"] = payload["label"]
        if "interval_minutes" in payload:
            interval = payload["interval_minutes"]
            if not isinstance(interval, int) or interval not in ALLOWED_INTERVALS:
                raise ValidationError("interval_minutes must be 1, 5, 15, or 60")
            updates["interval_minutes"] = interval
            updates["next_check_at"] = utc_now() + timedelta(minutes=interval)
        if "enabled" in payload:
            enabled = bool(payload["enabled"])
            updates["enabled"] = enabled
            if enabled and monitor.next_check_at is None:
                updates["next_check_at"] = utc_now()
        if not updates:
            return monitor
        updated = await self._monitors().update_fields(monitor_id, **updates)
        await AuditService(self.registry).record_domain(
            action="health_monitor.updated",
            resource_type="health_monitor",
            resource_id=monitor_id,
            actor_id=actor_id,
        )
        return updated

    async def delete_monitor(
        self,
        monitor_id: int,
        actor_id: int,
        *,
        is_superuser: bool = False,
    ) -> None:
        await self._get_owned(monitor_id, actor_id, is_superuser=is_superuser)
        await self._results().delete_for_monitor(monitor_id)
        await self._monitors().delete(monitor_id)
        await AuditService(self.registry).record_domain(
            action="health_monitor.deleted",
            resource_type="health_monitor",
            resource_id=monitor_id,
            actor_id=actor_id,
        )

    async def get_history(
        self,
        monitor_id: int,
        actor_id: int,
        *,
        is_superuser: bool = False,
        hours: int = HISTORY_HOURS,
    ) -> HealthHistoryResponse:
        await self._get_owned(monitor_id, actor_id, is_superuser=is_superuser)
        since = utc_now() - timedelta(hours=hours)
        results = await self._results().list_for_monitor(
            monitor_id,
            since=since,
            limit=HISTORY_MAX_POINTS,
        )
        return HealthHistoryResponse(
            items=[HealthHistoryPoint.model_validate(r) for r in results]
        )

    async def run_check(self, monitor_id: int) -> HealthMonitor:
        """Probe a monitor and persist the result (no ownership check)."""
        monitor = await self._monitors().get(monitor_id)
        outcome = await probe_url(monitor.url)
        now = utc_now()
        result = HealthCheckResult(
            monitor_id=monitor.id,
            checked_at=now,
            status_code=outcome.status_code,
            response_ms=outcome.response_ms,
            ok=outcome.ok,
            error=outcome.error,
            ssl_expires_at=outcome.ssl_expires_at,
        )
        await self._results().insert(result)
        ok_count, total = await self._results().count_uptime(monitor.id)
        uptime = compute_uptime_percent(ok_count, total)
        next_check = now + timedelta(minutes=monitor.interval_minutes)
        return await self._monitors().update_fields(
            monitor.id,
            last_checked_at=now,
            last_status_code=outcome.status_code,
            last_response_ms=outcome.response_ms,
            last_ok=outcome.ok,
            last_error=outcome.error,
            uptime_percent=uptime,
            ssl_expires_at=outcome.ssl_expires_at,
            dns=[d.model_dump() for d in outcome.dns],
            next_check_at=next_check,
        )

    async def check_now(
        self,
        monitor_id: int,
        actor_id: int,
        *,
        is_superuser: bool = False,
    ) -> HealthMonitor:
        await self._get_owned(monitor_id, actor_id, is_superuser=is_superuser)
        return await self.run_check(monitor_id)

    async def run_due_checks(self, *, limit: int = MAX_CHECKS_PER_TICK) -> int:
        """Probe due monitors; return how many were checked."""
        now = utc_now()
        due = await self._monitors().list_due(now=now, limit=limit)
        checked = 0
        for monitor in due:
            await self.run_check(monitor.id)
            checked += 1
        return checked

    async def cleanup_old_results(
        self, *, retention_days: int = CLEANUP_RETENTION_DAYS
    ) -> int:
        """Delete results older than retention window."""
        cutoff = utc_now() - timedelta(days=retention_days)
        return await self._results().delete_older_than(cutoff)
