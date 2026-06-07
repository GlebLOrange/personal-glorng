"""YouTube download tool. Public endpoint with strict rate and concurrency limits."""

import asyncio
import mimetypes
import shutil
import tempfile
import time
from collections import defaultdict
from collections.abc import Generator
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.core.deps import OptionalUser
from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.permissions import permission_key, user_has_permission
from app.core.rate_limit import rate_limit_api, rate_limit_vid_download
from app.core.utils import attachment_content_disposition
from app.schemas.viddownload import VidDownloadRequest

router = APIRouter(
    prefix="/vid-download",
    tags=["vid-download"],
    dependencies=[Depends(rate_limit_api)],
)

DOWNLOAD_TIMEOUT = 120
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_CONCURRENT_DOWNLOADS = 2
MAX_CONCURRENT_PER_IP = 1

_active_downloads = 0
_download_lock = asyncio.Lock()
_ip_active_downloads: defaultdict[str, int] = defaultdict(int)
_ip_lock = asyncio.Lock()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _acquire_ip_slot(client_ip: str) -> None:
    async with _ip_lock:
        if _ip_active_downloads[client_ip] >= MAX_CONCURRENT_PER_IP:
            raise ApiError(
                503,
                "Too many concurrent downloads from your IP, try again later",
            )
        _ip_active_downloads[client_ip] += 1


async def _release_ip_slot(client_ip: str) -> None:
    async with _ip_lock:
        current = _ip_active_downloads.get(client_ip, 0)
        if current <= 1:
            _ip_active_downloads.pop(client_ip, None)
        else:
            _ip_active_downloads[client_ip] = current - 1


async def _acquire_global_slot() -> None:
    global _active_downloads
    async with _download_lock:
        if _active_downloads >= MAX_CONCURRENT_DOWNLOADS:
            raise ApiError(
                503,
                "Server busy — too many concurrent downloads, try again later",
            )
        _active_downloads += 1


async def _release_global_slot() -> None:
    global _active_downloads
    async with _download_lock:
        _active_downloads = max(0, _active_downloads - 1)


def _build_command(data: VidDownloadRequest, tmp_dir: str) -> list[str]:
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
    cmd.append(str(data.url))
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
    description="Public YouTube download (rate limited).",
    dependencies=[Depends(rate_limit_vid_download)],
)
async def download_video(
    data: VidDownloadRequest,
    request: Request,
    user: OptionalUser,
) -> StreamingResponse:
    client_ip = _client_ip(request)
    url_host = urlparse(str(data.url)).hostname or "unknown"
    privileged = user is not None and user_has_permission(
        user, permission_key("vid-download", "write")
    )

    await _acquire_ip_slot(client_ip)
    await _acquire_global_slot()
    started = time.monotonic()

    try:
        tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
        try:
            cmd = _build_command(data, tmp_dir)
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
                    "ip": client_ip,
                    "url_host": url_host,
                    "file_size": file_size,
                    "duration_s": round(time.monotonic() - started, 2),
                    "privileged": privileged,
                },
            )

            return StreamingResponse(
                _stream_and_cleanup(target, tmp_dir),
                media_type=mime or "application/octet-stream",
                headers={
                    "Content-Disposition": attachment_content_disposition(
                        target.name
                    ),
                    "Content-Length": str(file_size),
                },
            )
        except Exception:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise
    finally:
        await _release_global_slot()
        await _release_ip_slot(client_ip)
