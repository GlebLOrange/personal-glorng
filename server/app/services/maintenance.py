"""Turnstile verification and host DB maintenance process control."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Literal

import httpx

from app.core.exceptions import ApiError, ConflictError
from app.settings import Settings

logger = logging.getLogger(__name__)

TURNSTILE_SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
MaintenanceStatus = Literal["idle", "running", "ok", "failed"]

_status: MaintenanceStatus = "idle"
_detail: str = ""
_process: asyncio.subprocess.Process | None = None
_watch_task: asyncio.Task[None] | None = None
_lock = asyncio.Lock()


def reset_maintenance_state() -> None:
    """Clear in-process status (tests only)."""
    global _status, _detail, _process, _watch_task
    _status = "idle"
    _detail = ""
    _process = None
    _watch_task = None


def get_maintenance_snapshot() -> tuple[MaintenanceStatus, str]:
    """Return the current status and detail message."""
    return _status, _detail


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


async def _watch_process(proc: asyncio.subprocess.Process) -> None:
    """Update status when the spawned maintenance process exits."""
    global _status, _detail, _process
    code = await proc.wait()
    async with _lock:
        if _process is not proc:
            return
        _process = None
        if code == 0:
            _status = "ok"
            _detail = "maintenance finished"
        else:
            _status = "failed"
            _detail = f"maintenance failed (exit {code}). check the server log before running it again"
            logger.error("db maintenance exited with code %s", code)


async def start_maintenance(settings: Settings) -> tuple[MaintenanceStatus, str]:
    """Spawn the configured maintenance script without a shell."""
    global _status, _detail, _process, _watch_task

    if not settings.db_maintenance_ready():
        raise ApiError(503, "Database maintenance is not available in this deploy")

    script = Path(settings.DB_MAINTENANCE_SCRIPT.strip())
    if not script.is_file():
        raise ApiError(503, "Database maintenance script is missing")

    async with _lock:
        if _status == "running" and _process is not None and _process.returncode is None:
            raise ConflictError("maintenance is already running. wait for it to finish")

        try:
            proc = await asyncio.create_subprocess_exec(
                str(script),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as exc:
            logger.exception("failed to start db maintenance")
            raise ApiError(500, "Could not start maintenance") from exc

        _process = proc
        _status = "running"
        _detail = "maintenance is running"
        _watch_task = asyncio.create_task(_watch_process(proc))
        return _status, _detail
