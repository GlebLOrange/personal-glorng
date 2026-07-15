import re
import secrets
import string
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

_ASCII_FILENAME_RE = re.compile(r"[^\x20-\x7E]+")


def utc_now() -> datetime:
    return datetime.now(UTC)


def as_utc(value: datetime) -> datetime:
    """Normalize DB datetimes to UTC-aware for comparisons."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def format_scheduled_at(value: datetime) -> str:
    """Format task scheduled time for display (UTC)."""
    return as_utc(value).strftime("%Y-%m-%d %H:%M")


def calendar_datetime(value: datetime) -> str:
    """RFC3339 UTC string for Google Calendar API."""
    return as_utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_short_code(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


DEFAULT_PER_PAGE = 9


def paginate_params(
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
) -> tuple[int, int]:
    page = max(1, page)
    per_page = min(max(1, per_page), 100)
    offset = (page - 1) * per_page
    return offset, per_page


def iter_file(path: Path, chunk_size: int = 64 * 1024) -> Generator[bytes]:
    """Yield file contents in chunks for streaming responses."""
    with open(path, "rb") as fh:
        while chunk := fh.read(chunk_size):
            yield chunk


def attachment_content_disposition(filename: str) -> str:
    """Build a safe Content-Disposition header for file downloads."""
    cleaned = filename.replace('"', "_").replace("\n", "_").replace("\r", "_")
    ascii_name = _ASCII_FILENAME_RE.sub("_", cleaned).strip() or "download"
    utf8_name = quote(filename, safe="")
    # Unquoted filename= avoids Starlette re-encoding embedded quotes.
    return f"attachment; filename={ascii_name}; filename*=UTF-8''{utf8_name}"
