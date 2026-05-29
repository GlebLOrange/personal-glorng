import secrets
import string
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path


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


def paginate_params(
    page: int = 1,
    per_page: int = 20,
) -> tuple[int, int]:
    page = max(1, page)
    per_page = min(max(1, per_page), 100)
    offset = (page - 1) * per_page
    return offset, per_page


def iter_file(path: Path, chunk_size: int = 64 * 1024) -> Generator[bytes, None, None]:
    """Yield file contents in chunks for streaming responses."""
    with open(path, "rb") as fh:
        while chunk := fh.read(chunk_size):
            yield chunk
