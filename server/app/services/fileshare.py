"""File share business logic."""

from datetime import timedelta
from pathlib import Path

from app.core.exceptions import ApiError, NotFoundError
from app.core.logging import logger
from app.core.utils import as_utc, generate_short_code, utc_now
from app.db.documents.fileshare import SharedFile
from app.db.registry import DatabaseRegistry
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


def _files(registry: DatabaseRegistry):
    if registry.files is None:
        msg = "File share repository is not initialized"
        raise RuntimeError(msg)
    return registry.files


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
    registry: DatabaseRegistry,
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
    shared = await _files(registry).insert(shared)

    await AuditService(registry).record_domain(
        action="file.uploaded",
        resource_type="file",
        resource_id=shared.id,
        actor_id=user_id,
        metadata={"code": shared.code, "filename": filename},
    )
    return shared


async def list_files(
    registry: DatabaseRegistry,
    *,
    offset: int = 0,
    limit: int = 20,
    user_id: int,
) -> list[SharedFile]:
    return await _files(registry).list(
        offset=offset,
        limit=limit,
        created_by=user_id,
        sort=[("created_at", -1)],
    )


async def delete(registry: DatabaseRegistry, *, file_id: int, user_id: int) -> None:
    """Remove file from disk and DB."""
    shared = await _files(registry).get_or_none(file_id)
    if not shared or shared.created_by != user_id:
        raise NotFoundError("File not found")

    disk_path = _shares_dir() / shared.file_path
    if disk_path.exists():
        disk_path.unlink()

    await _files(registry).delete(file_id)

    await AuditService(registry).record_domain(
        action="file.deleted",
        resource_type="file",
        resource_id=file_id,
        actor_id=user_id,
    )


async def get_by_code(
    registry: DatabaseRegistry,
    *,
    code: str,
) -> tuple[SharedFile, Path]:
    """Look up shared file by code, validate expiry, increment downloads."""
    shared = await _files(registry).get_by_code(code)
    if not shared:
        raise NotFoundError("File not found")

    if utc_now() > as_utc(shared.expires_at):
        raise ApiError(410, "This file has expired")

    disk_path = _shares_dir() / shared.file_path
    if not disk_path.exists():
        raise NotFoundError("File not found on disk")

    await _files(registry).update_fields(shared.id, downloads=shared.downloads + 1)

    return shared, disk_path


async def cleanup_expired(registry: DatabaseRegistry) -> dict[str, int]:
    """Remove expired shared files from disk and database."""
    now = utc_now()
    all_files = await _files(registry).list(limit=10_000)
    expired = [shared for shared in all_files if as_utc(shared.expires_at) < now]

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
        await _files(registry).delete(shared.id)
        deleted_rows += 1

    return {
        "deleted_rows": deleted_rows,
        "deleted_files": deleted_files,
        "errors": errors,
    }
