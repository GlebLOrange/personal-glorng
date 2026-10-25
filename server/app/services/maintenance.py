"""Turnstile verification and multi-job maintenance control."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Literal

import httpx

from app.core.email import get_email_backend, render_plain_text
from app.core.exceptions import ApiError, ConflictError, ForbiddenError
from app.schemas.maintenance import MaintenanceJob
from app.settings import Settings

logger = logging.getLogger(__name__)

TURNSTILE_SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
MaintenanceStatus = Literal["idle", "running", "ok", "failed"]
_HOST_JOBS: frozenset[MaintenanceJob] = frozenset({"backup", "stale"})
_INPROC_JOBS: frozenset[MaintenanceJob] = frozenset({"sync", "cleanup", "seed"})

_status: MaintenanceStatus = "idle"
_detail: str = ""
_job: str = ""
_report: str = ""
_process: asyncio.subprocess.Process | None = None
_watch_task: asyncio.Task[None] | None = None
_lock = asyncio.Lock()


@dataclass(frozen=True, slots=True)
class MaintenanceSnapshot:
    """In-memory maintenance panel state."""

    status: MaintenanceStatus
    detail: str
    job: str = ""
    report: str = ""


def reset_maintenance_state() -> None:
    """Clear in-process status (tests only)."""
    global _status, _detail, _job, _report, _process, _watch_task
    _status = "idle"
    _detail = ""
    _job = ""
    _report = ""
    _process = None
    _watch_task = None


def get_maintenance_snapshot() -> MaintenanceSnapshot:
    """Return the current status snapshot."""
    return MaintenanceSnapshot(
        status=_status,
        detail=_detail,
        job=_job,
        report=_report,
    )


def maintenance_seed_allowed(settings: Settings) -> bool:
    """Whether the seed job may run from the admin panel."""
    if settings.MAINTENANCE_SEED_ENABLED:
        return True
    return settings.APP_ENV != "production"


async def verify_turnstile_token(
    settings: Settings,
    token: str,
    *,
    remote_ip: str | None = None,
) -> None:
    """Verify a Turnstile token with Cloudflare siteverify."""
    secret = settings.TURNSTILE_SECRET_KEY.strip()
    if not secret or not settings.TURNSTILE_SITE_KEY.strip():
        raise ApiError(503, "Turnstile is not configured")
    cleaned = token.strip()
    if not cleaned:
        raise ApiError(400, "Turnstile token is required")

    payload: dict[str, str] = {"secret": secret, "response": cleaned}
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(TURNSTILE_SITEVERIFY_URL, data=payload)
            resp.raise_for_status()
            body = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Turnstile siteverify failed", exc_info=exc)
        raise ApiError(502, "Could not verify captcha") from exc

    if not bool(body.get("success")):
        raise ApiError(400, "Captcha verification failed")


async def _send_report_email(
    settings: Settings,
    job: str,
    *,
    ok: bool,
    report: str,
) -> None:
    """Email ALLOWED_EMAIL with the job outcome. Never fails the job."""
    status_label = "ok" if ok else "failed"
    subject = f"Maintenance {job}: {status_label}"
    lines = [line for line in report.splitlines() if line.strip()] or [report or status_label]
    plain = render_plain_text(subject, lines)
    html_body = "".join(
        f'<p style="margin:0 0 8px;font-family:monospace;font-size:13px;">'
        f"{escape(line)}</p>"
        for line in lines
    )
    html = (
        "<!DOCTYPE html><html><body style=\"margin:0;padding:16px;\" "
        f"background:#111827;color:#d1d5db;\">"
        f"<h1 style=\"font-size:18px;\">{escape(subject)}</h1>{html_body}</body></html>"
    )
    try:
        await get_email_backend().send(settings.ALLOWED_EMAIL, subject, html, plain)
    except Exception:
        logger.warning(
            "maintenance report email failed",
            exc_info=True,
            extra={"job": job, "ok": ok},
        )


async def _finish(
    settings: Settings,
    job: str,
    *,
    ok: bool,
    detail: str,
    report: str,
) -> None:
    """Set terminal status and email the operator."""
    global _status, _detail, _report
    async with _lock:
        _status = "ok" if ok else "failed"
        _detail = detail
        _report = report
    await _send_report_email(settings, job, ok=ok, report=report)


async def _watch_process(
    proc: asyncio.subprocess.Process,
    settings: Settings,
    job: str,
) -> None:
    """Update status when the spawned host script exits."""
    global _process
    code = await proc.wait()
    async with _lock:
        if _process is not proc:
            return
        _process = None
    if code == 0:
        report = f"{job}: host script finished (exit 0)"
        await _finish(
            settings,
            job,
            ok=True,
            detail=f"{job} finished",
            report=report,
        )
        return
    report = f"{job}: host script failed (exit {code})"
    logger.error("maintenance job %s exited with code %s", job, code)
    await _finish(
        settings,
        job,
        ok=False,
        detail=(
            f"{job} failed (exit {code}). "
            "check the server log before running it again"
        ),
        report=report,
    )


async def _run_inproc_job(settings: Settings, job: MaintenanceJob) -> None:
    """Run sync, cleanup, or seed inside the API process."""
    try:
        if job == "sync":
            from app.workers.tasks import process_sync_queue

            await process_sync_queue()
            report = "sync: drained pending calendar queue batch (max 10)"
        elif job == "cleanup":
            from app.workers.tasks import (
                cleanup_expired_shares,
                cleanup_health_results,
                cleanup_old_tasks,
            )

            await cleanup_old_tasks()
            await cleanup_expired_shares()
            await cleanup_health_results()
            report = "cleanup: old tasks, expired shares, health results"
        elif job == "seed":
            from app.db.seed import seed

            await seed()
            report = "seed: admin + demo mock data applied"
        else:
            report = f"{job}: unknown in-process job"
            await _finish(
                settings,
                job,
                ok=False,
                detail=report,
                report=report,
            )
            return

        await _finish(
            settings,
            job,
            ok=True,
            detail=f"{job} finished",
            report=report,
        )
    except Exception as exc:
        logger.exception("maintenance in-process job %s failed", job)
        report = f"{job}: failed — {exc!s}"[:500]
        await _finish(
            settings,
            job,
            ok=False,
            detail=f"{job} failed. check the server log before running it again",
            report=report,
        )


def _assert_not_running() -> None:
    """Raise if another maintenance job is still running."""
    if (
        _status == "running"
        and _process is not None
        and _process.returncode is None
    ):
        raise ConflictError("maintenance is already running. wait for it to finish")
    if _status == "running" and _watch_task is not None and not _watch_task.done():
        raise ConflictError("maintenance is already running. wait for it to finish")


async def start_maintenance(
    settings: Settings,
    job: MaintenanceJob,
) -> MaintenanceSnapshot:
    """Start a named maintenance job (host script or in-process)."""
    global _status, _detail, _job, _report, _process, _watch_task

    if not settings.turnstile_configured():
        raise ApiError(503, "Turnstile is not configured")

    if job in _HOST_JOBS:
        if not settings.db_maintenance_ready():
            raise ApiError(
                503,
                "Host maintenance script is not available in this deploy",
            )
        script = Path(settings.DB_MAINTENANCE_SCRIPT.strip())
        if not script.is_file():
            raise ApiError(503, "Database maintenance script is missing")

        async with _lock:
            _assert_not_running()
            cmd = [str(script)]
            if job == "stale":
                cmd.append("--check-stale")
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
            except OSError as exc:
                logger.exception("failed to start maintenance job %s", job)
                raise ApiError(500, "Could not start maintenance") from exc

            _process = proc
            _status = "running"
            _job = job
            _report = ""
            _detail = f"{job} is running"
            _watch_task = asyncio.create_task(_watch_process(proc, settings, job))
            return get_maintenance_snapshot()

    if job not in _INPROC_JOBS:
        raise ApiError(400, f"Unknown maintenance job: {job}")

    if job == "seed" and not maintenance_seed_allowed(settings):
        raise ForbiddenError(
            "seed is disabled in production "
            "(set MAINTENANCE_SEED_ENABLED=true to override)"
        )

    async with _lock:
        _assert_not_running()
        _status = "running"
        _job = job
        _report = ""
        _detail = f"{job} is running"
        _process = None
        _watch_task = asyncio.create_task(_run_inproc_job(settings, job))
        return get_maintenance_snapshot()
