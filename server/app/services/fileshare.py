"""File share business logic."""

from datetime import timedelta
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApiError, NotFoundError
from app.core.logging import logger
from app.core.utils import as_utc, generate_short_code, utc_now
from app.db.models.shared_file import SharedFile
from app.services.audit import AuditService
from app.settings import get_settings

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB
EXPIRY_HOURS = 24
_BLOCKED_EXTENSIONS = frozenset(
    {
        ".html",
        ".htm",
        ".xhtml",
        ".svg",
        ".exe",
        ".bat",
        ".cmd",
        ".sh",
        ".js",
        ".mjs",
        ".cjs",
        ".vbs",
        ".ps1",
        ".php",
        ".aspx",
    }
)
_DOWNLOAD_SAFE_TYPES = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "text/plain",
        "application/zip",
        "application/gzip",
    }
)


def _shares_dir() -> Path:
    return Path(get_settings().MEDIA_DIR) / "shares"


def _sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in ".-_" else "_" for c in name)[:100]


def _blocked_extension(filename: str) -> str | None:
    """Return blocked extension if any suffix in the filename is denied."""
    parts = Path(filename).name.lower().split(".")
    for suffix in parts[1:]:
        ext = f".{suffix}"
        if ext in _BLOCKED_EXTENSIONS:
            return ext
    return None


def _sniff_content_type(contents: bytes, filename: str) -> str:
    """Detect MIME from magic bytes; avoid trusting client-supplied types."""
    if contents.startswith(b"%PDF"):
        return "application/pdf"
    if contents.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if contents[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if contents.startswith(b"GIF87a") or contents.startswith(b"GIF89a"):
        return "image/gif"
    if contents.startswith(b"PK\x03\x04"):
        return "application/zip"
    ext = Path(filename).suffix.lower()
    ext_map = {
        ".txt": "text/plain",
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".zip": "application/zip",
        ".gz": "application/gzip",
    }
    return ext_map.get(ext, "application/octet-stream")


def download_media_type(stored_type: str) -> str:
    """Serve only known-safe MIME types; force octet-stream otherwise."""
    if stored_type in _DOWNLOAD_SAFE_TYPES:
        return stored_type
    return "application/octet-stream"


async def upload(
    db: AsyncSession,
    *,
    filename: str,
    contents: bytes,
    user_id: int,
) -> SharedFile:
    """Store file on disk and create DB record."""
    if len(contents) > MAX_UPLOAD_SIZE:
        raise ApiError(413, f"File exceeds {MAX_UPLOAD_SIZE // (1024 * 1024)} MB limit")

    blocked = _blocked_extension(filename)
    if blocked:
        raise ApiError(400, f"File type '{blocked}' is not allowed")

    code = generate_short_code(6)
    stored_name = f"{code}_{_sanitize_filename(filename)}"
    safe_type = _sniff_content_type(contents, filename)

    dest = _shares_dir()
    dest.mkdir(parents=True, exist_ok=True)
    (dest / stored_name).write_bytes(contents)

    shared = SharedFile(
        code=code,
        original_filename=filename[:255],
        file_path=stored_name,
        file_size=len(contents),
        content_type=safe_type,
        downloads=0,
        expires_at=utc_now() + timedelta(hours=EXPIRY_HOURS),
        created_by=user_id,
    )
    db.add(shared)
    await db.flush()
    await db.refresh(shared)

    await AuditService(db).record_domain(
        action="file.uploaded",
        resource_type="file",
        resource_id=shared.id,
        actor_id=user_id,
        metadata={"code": shared.code, "filename": filename},
    )
    return shared


async def list_files(
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 20,
    user_id: int,
) -> list[SharedFile]:
    result = await db.execute(
        select(SharedFile)
        .where(SharedFile.created_by == user_id)
        .order_by(SharedFile.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


async def delete(db: AsyncSession, *, file_id: int, user_id: int) -> None:
    """Remove file from disk and DB."""
    result = await db.execute(select(SharedFile).where(SharedFile.id == file_id))
    shared = result.scalar_one_or_none()
    if not shared:
        raise NotFoundError("File not found")
    if shared.created_by != user_id:
        raise NotFoundError("File not found")

    disk_path = _shares_dir() / shared.file_path
    if disk_path.exists():
        disk_path.unlink()

    await db.delete(shared)
    await db.flush()

    await AuditService(db).record_domain(
        action="file.deleted",
        resource_type="file",
        resource_id=file_id,
        actor_id=user_id,
    )


async def get_by_code(db: AsyncSession, *, code: str) -> tuple[SharedFile, Path]:
    """Look up shared file by code, validate expiry, increment downloads."""
    result = await db.execute(select(SharedFile).where(SharedFile.code == code))
    shared = result.scalar_one_or_none()
    if not shared:
        raise NotFoundError("File not found")

    if utc_now() > as_utc(shared.expires_at):
        raise ApiError(410, "This file has expired")

    disk_path = _shares_dir() / shared.file_path
    if not disk_path.exists():
        raise NotFoundError("File not found on disk")

    await db.execute(
        update(SharedFile)
        .where(SharedFile.id == shared.id)
        .values(downloads=SharedFile.downloads + 1)
    )
    await db.flush()

    return shared, disk_path


async def cleanup_expired(db: AsyncSession) -> dict[str, int]:
    """Remove expired shared files from disk and database."""
    now = utc_now()
    result = await db.execute(select(SharedFile).where(SharedFile.expires_at < now))
    expired = list(result.scalars().all())

    deleted_rows = 0
    deleted_files = 0
    errors = 0
    shares_dir = _shares_dir()

    for shared in expired:
        disk_path = shares_dir / shared.file_path
        try:
            if disk_path.exists():
                disk_path.unlink()
                deleted_files += 1
        except OSError as exc:
            errors += 1
            logger.error(
                "Failed to delete expired share file",
                error=exc,
                context={"file_id": shared.id, "path": str(disk_path)},
            )
        await db.delete(shared)
        deleted_rows += 1

    if deleted_rows:
        await db.flush()

    return {
        "deleted_rows": deleted_rows,
        "deleted_files": deleted_files,
        "errors": errors,
    }
