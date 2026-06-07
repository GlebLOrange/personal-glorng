"""Smoke test for expired file-share cleanup worker."""

from unittest.mock import AsyncMock, patch

import pytest

from app.workers.tasks import cleanup_expired_shares


@pytest.mark.asyncio
async def test_cleanup_expired_shares_worker_invokes_service() -> None:
    mock_cleanup = AsyncMock(
        return_value={"deleted_rows": 2, "deleted_files": 2, "errors": 0}
    )
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    with (
        patch(
            "app.workers.tasks.get_session_factory", return_value=lambda: mock_session
        ),
        patch("app.services.fileshare.cleanup_expired", mock_cleanup),
    ):
        await cleanup_expired_shares()

    mock_cleanup.assert_awaited_once_with(mock_session)
    mock_session.commit.assert_awaited_once()
