"""File share business logic."""

from datetime import timedelta
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApiError, NotFoundError
from app.core.utils import generate_short_code, utc_now
from app.db.models.audit_event import AuditActorType, AuditCategory, AuditSource
from app.db.models.shared_file import SharedFile
from app.services.audit import AuditRecord, AuditService
from app.settings import get_settings

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB
EXPIRY_HOURS = 24
_BLOCKED_EXTENSIONS = frozenset(
    {
        ".html",
        ".htm",
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
    }
)


def _shares_dir() -> Path:
    return Path(get_settings().MEDIA_DIR) / "shares"


def _sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in ".-_" else "_" for c in name)[:100]


async def upload(
    db: AsyncSession,
    *,
    filename: str,
    contents: bytes,
    content_type: str,
    user_id: int,
) -> SharedFile:
    """Store file on disk and create DB record."""
    if len(contents) > MAX_UPLOAD_SIZE:
        raise ApiError(413, f"File exceeds {MAX_UPLOAD_SIZE // (1024 * 1024)} MB limit")

    ext = Path(filename).suffix.lower()
    if ext in _BLOCKED_EXTENSIONS:
        raise ApiError(400, f"File type '{ext}' is not allowed")

    code = generate_short_code(6)
    stored_name = f"{code}_{_sanitize_filename(filename)}"

    dest = _shares_dir()
    dest.mkdir(parents=True, exist_ok=True)
    (dest / stored_name).write_bytes(contents)

    shared = SharedFile(
        code=code,
        original_filename=filename[:255],
        file_path=stored_name,
        file_size=len(contents),
        content_type=content_type,
        downloads=0,
        expires_at=utc_now() + timedelta(hours=EXPIRY_HOURS),
        created_by=user_id,
    )
    db.add(shared)
    await db.flush()
    await db.refresh(shared)

    await AuditService(db).record(
        AuditRecord(
            category=AuditCategory.DOMAIN,
            action="file.uploaded",
            actor_type=AuditActorType.USER,
            actor_id=user_id,
            source=AuditSource.WEB_ADMIN,
            resource_type="file",
            resource_id=shared.id,
            metadata={"code": shared.code, "filename": filename},
        ),
    )
    return shared


async def list_files(
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 20,
) -> list[SharedFile]:
    result = await db.execute(
        select(SharedFile)
        .order_by(SharedFile.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


async def delete(db: AsyncSession, *, file_id: int) -> None:
    """Remove file from disk and DB."""
    result = await db.execute(select(SharedFile).where(SharedFile.id == file_id))
    shared = result.scalar_one_or_none()
    if not shared:
        raise NotFoundError("File not found")

    disk_path = _shares_dir() / shared.file_path
    if disk_path.exists():
        disk_path.unlink()

    await db.delete(shared)
    await db.flush()

    await AuditService(db).record(
        AuditRecord(
            category=AuditCategory.DOMAIN,
            action="file.deleted",
            actor_type=AuditActorType.USER,
            source=AuditSource.WEB_ADMIN,
            resource_type="file",
            resource_id=file_id,
        ),
    )


async def get_by_code(db: AsyncSession, *, code: str) -> tuple[SharedFile, Path]:
    """Look up shared file by code, validate expiry, increment downloads."""
    result = await db.execute(select(SharedFile).where(SharedFile.code == code))
    shared = result.scalar_one_or_none()
    if not shared:
        raise NotFoundError("File not found")

    if utc_now() > shared.expires_at.replace(tzinfo=utc_now().tzinfo):
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
