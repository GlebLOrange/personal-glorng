from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.core.exceptions import ApiError
from app.core.utils import as_utc
from app.db.documents.fileshare import SharedFile
from app.db.registry import DatabaseRegistry
from app.services import fileshare as fileshare_service
from tests.factories import create_user


@pytest.mark.asyncio
async def test_as_utc_handles_naive_datetime() -> None:
    naive = datetime(2026, 1, 1, 12, 0, 0)
    aware = as_utc(naive)
    assert aware.tzinfo == UTC
    assert aware.hour == 12


@pytest.mark.asyncio
async def test_as_utc_converts_non_utc_aware_datetime() -> None:
    warsaw = timezone(timedelta(hours=1))
    aware = datetime(2026, 1, 1, 13, 0, 0, tzinfo=warsaw)
    converted = as_utc(aware)
    assert converted.tzinfo == UTC
    assert converted.hour == 12


@pytest.mark.asyncio
async def test_get_by_code_expired_naive_datetime(registry: DatabaseRegistry) -> None:
    user = await create_user(registry)
    shared = SharedFile(
        code="abc123",
        original_filename="test.txt",
        file_path="abc123_test.txt",
        file_size=10,
        content_type="text/plain",
        downloads=0,
        expires_at=datetime(2020, 1, 1, 0, 0, 0),
        created_by=user.id,
    )
    assert registry.files is not None
    await registry.files.insert(shared)

    shares_dir = fileshare_service._shares_dir()
    shares_dir.mkdir(parents=True, exist_ok=True)
    (shares_dir / shared.file_path).write_bytes(b"hello")

    with pytest.raises(ApiError) as exc_info:
        await fileshare_service.get_by_code(registry, code="abc123")

    assert exc_info.value.status_code == 410
