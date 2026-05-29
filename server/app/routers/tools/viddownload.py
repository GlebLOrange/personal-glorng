import asyncio
import mimetypes
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import AuthorizedUser, require_capability
from app.core.exceptions import ApiError
from app.core.rate_limit import rate_limit_api
from app.schemas.viddownload import VidDownloadRequest

router = APIRouter(
    prefix="/vid-download",
    dependencies=[
        Depends(require_capability("vid-download", "read")),
        Depends(rate_limit_api),
    ],
)

DOWNLOAD_TIMEOUT = 120
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_CONCURRENT_DOWNLOADS = 2

_download_semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)


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


def _stream_and_cleanup(path: Path, tmp_dir: str) -> Generator[bytes, None, None]:
    try:
        with open(path, "rb") as fh:
            while chunk := fh.read(64 * 1024):
                yield chunk
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.post(
    "",
    dependencies=[Depends(require_capability("vid-download", "write"))],
)
async def download_video(
    data: VidDownloadRequest,
    user: AuthorizedUser,  # noqa: ARG001
) -> StreamingResponse:
    if not _download_semaphore._value:
        raise ApiError(
            503, "Server busy — too many concurrent downloads, try again later"
        )

    async with _download_semaphore:
        tmp_dir = tempfile.mkdtemp(prefix="ytdlp_")
        try:
            cmd = _build_command(data, tmp_dir)
            _stdout, stderr, returncode = await _run_download(cmd)

            if returncode != 0:
                err_msg = stderr.decode(errors="replace").strip()[-500:]
                raise ApiError(502, f"yt-dlp failed: {err_msg}")

            target = _find_output_file(tmp_dir)
            mime, _ = mimetypes.guess_type(target.name)

            return StreamingResponse(
                _stream_and_cleanup(target, tmp_dir),
                media_type=mime or "application/octet-stream",
                headers={
                    "Content-Disposition": f'attachment; filename="{target.name}"',
                    "Content-Length": str(target.stat().st_size),
                },
            )
        except Exception:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise
