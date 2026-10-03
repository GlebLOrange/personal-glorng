"""Video download via yt-dlp (authenticated; rate and concurrency limits)."""

import asyncio
import mimetypes
import shutil
import tempfile
import time
from collections.abc import Generator
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.core.deps import AuthorizedUser, require_capability
from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.rate_limit import client_ip, rate_limit_api, rate_limit_vid_download
from app.core.redis_keys import VID_DOWNLOAD_GLOBAL_KEY, VID_DOWNLOAD_IP_PREFIX
from app.core.redis_slots import release_slot, try_acquire_slot
from app.core.url_safety import get_public_http_url, is_public_http_url
from app.core.utils import attachment_content_disposition
from app.openapi import requires_capability
from app.schemas.viddownload import VidDownloadRequest, is_allowed_viddownload_host

router = APIRouter(
    prefix="/vid-download",
    tags=["vid-download"],
    dependencies=[
        Depends(require_capability("vid-download", "write")),
        Depends(rate_limit_api),
    ],
)

DOWNLOAD_TIMEOUT = 120
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_CONCURRENT_DOWNLOADS = 2
MAX_CONCURRENT_PER_IP = 1
# TTL backstop if a worker crashes before release (timeout + margin).
_SLOT_TTL_SEC = DOWNLOAD_TIMEOUT + 60


def _ip_slot_key(ip_address: str) -> str:
    return f"{VID_DOWNLOAD_IP_PREFIX}{ip_address}"


async def _acquire_ip_slot(ip_address: str) -> None:
    acquired = await try_acquire_slot(
        _ip_slot_key(ip_address),
        limit=MAX_CONCURRENT_PER_IP,
        ttl=_SLOT_TTL_SEC,
    )
    if acquired is None:
        raise ApiError(503, "Service temporarily unavailable")
    if not acquired:
        raise ApiError(
            503,
            "Too many concurrent downloads from your IP, try again later",
        )


async def _release_ip_slot(ip_address: str) -> None:
    await release_slot(_ip_slot_key(ip_address))


async def _acquire_global_slot() -> None:
    acquired = await try_acquire_slot(
        VID_DOWNLOAD_GLOBAL_KEY,
        limit=MAX_CONCURRENT_DOWNLOADS,
        ttl=_SLOT_TTL_SEC,
    )
    if acquired is None:
        raise ApiError(503, "Service temporarily unavailable")
    if not acquired:
        raise ApiError(
            503,
            "Server busy — too many concurrent downloads, try again later",
        )


async def _release_global_slot() -> None:
    await release_slot(VID_DOWNLOAD_GLOBAL_KEY)


async def _resolve_public_download_url(url: str) -> str:
    """Follow redirects with the same SSRF checks as other server-side fetches."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await get_public_http_url(client, url)
        resolved = str(response.url)
        await response.aclose()
    if not is_public_http_url(resolved):
        raise ApiError(422, "URL must be a public http(s) address")
    if not is_allowed_viddownload_host(resolved):
        raise ApiError(422, "URL host is not an allowed video platform")
    return resolved


def _build_command(
    resolved_url: str,
    data: VidDownloadRequest,
    tmp_dir: str,
) -> list[str]:
    # ponytail: pinned yt-dlp has no --max-redirects CLI flag; redirect
    # budget is enforced in _resolve_public_download_url via get_public_http_url.
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--no-overwrites",
        "--restrict-filenames",
        "--no-cache-dir",
        "--max-filesize",
        "500M",
        "-o",
        f"{tmp_dir}/%(title).80s.%(ext)s",
        "-f",
        data.format,
    ]
    if data.audio_only:
        cmd += ["-x", "--audio-format", "mp3"]
    cmd.append(resolved_url)
    return cmd


async def _run_download(cmd: list[str]) -> tuple[bytes, bytes, int]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=DOWNLOAD_TIMEOUT
        )
    except TimeoutError:
        proc.kill()
        await proc.wait()
        raise ApiError(504, "Download timed out") from None
    return stdout, stderr, proc.returncode or 0


def _find_output_file(tmp_dir: str) -> Path:
    files = [
        f for f in Path(tmp_dir).iterdir() if f.is_file() and not f.name.startswith(".")
    ]
    if not files:
        raise ApiError(502, "yt-dlp produced no output file")
    target = max(files, key=lambda f: f.stat().st_size)
    if target.stat().st_size > MAX_FILE_SIZE:
        raise ApiError(
            413, f"Downloaded file exceeds {MAX_FILE_SIZE // (1024 * 1024)} MB limit"
        )
    return target


def _stream_and_cleanup(path: Path, tmp_dir: str) -> Generator[bytes]:
    try:
        with open(path, "rb") as fh:
            while chunk := fh.read(64 * 1024):
                yield chunk
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.post(
    "",
    summary="Download video via yt-dlp",
    description=requires_capability("vid-download", "write"),
    dependencies=[Depends(rate_limit_vid_download)],
)
async def download_video(
    data: VidDownloadRequest,
    request: Request,
    user: AuthorizedUser,
) -> StreamingResponse:
    request_ip = client_ip(request)
    url_host = urlparse(str(data.url)).hostname or "unknown"

    await _acquire_ip_slot(request_ip)
    try:
        await _acquire_global_slot()
    except Exception:
        await _release_ip_slot(request_ip)
        raise
    started = time.monotonic()

    try:
        tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
        try:
            try:
                resolved_url = await _resolve_public_download_url(str(data.url))
            except ValueError as exc:
                raise ApiError(422, str(exc)) from exc
            cmd = _build_command(resolved_url, data, tmp_dir)
            _stdout, stderr, returncode = await _run_download(cmd)

            if returncode != 0:
                err_msg = stderr.decode(errors="replace").strip()[-500:]
                raise ApiError(502, f"yt-dlp failed: {err_msg}")

            target = _find_output_file(tmp_dir)
            mime, _ = mimetypes.guess_type(target.name)
            file_size = target.stat().st_size

            logger.info(
                "Video download completed",
                context={
                    "ip": request_ip,
                    "url_host": url_host,
                    "file_size": file_size,
                    "duration_s": round(time.monotonic() - started, 2),
                    "user_id": str(user.id),
                },
            )

            return StreamingResponse(
                _stream_and_cleanup(target, tmp_dir),
                media_type=mime or "application/octet-stream",
                headers={
                    "Content-Disposition": attachment_content_disposition(target.name),
                    "Content-Length": str(file_size),
                },
            )
        except Exception:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise
    finally:
        await _release_global_slot()
        await _release_ip_slot(request_ip)
