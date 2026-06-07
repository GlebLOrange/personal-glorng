"""Smoke test for expired file-share cleanup worker."""

from unittest.mock import AsyncMock, patch

import pytest

from app.db.registry import DatabaseRegistry
from app.workers.tasks import cleanup_expired_shares


@pytest.mark.asyncio
async def test_cleanup_expired_shares_worker_invokes_service(
    registry: DatabaseRegistry,
) -> None:
    mock_cleanup = AsyncMock(
        return_value={"deleted_rows": 2, "deleted_files": 2, "errors": 0}
    )

    with (
        patch(
            "app.workers.tasks.get_worker_registry",
            new_callable=AsyncMock,
            return_value=registry,
        ),
        patch("app.services.fileshare.cleanup_expired", mock_cleanup),
    ):
        await cleanup_expired_shares()

    mock_cleanup.assert_awaited_once_with(registry)
