"""Tests for Celery job queue sanitization."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.workers.job_names import JobName
from app.workers.queue import CeleryJobQueue


@pytest.fixture
def queue() -> CeleryJobQueue:
    return CeleryJobQueue(MagicMock())


@pytest.mark.asyncio
async def test_enqueue_rejects_invalid_email(queue: CeleryJobQueue) -> None:
    result = await queue.enqueue(JobName.SEND_VERIFICATION_EMAIL, "", "token")
    assert result is None


@pytest.mark.asyncio
async def test_enqueue_rejects_invalid_reminder_id(queue: CeleryJobQueue) -> None:
    result = await queue.enqueue(JobName.SEND_REMINDER, 0)
    assert result is None


@pytest.mark.asyncio
@patch("app.workers.queue.asyncio.to_thread")
async def test_enqueue_applies_eta_for_reminder(
    mock_to_thread: MagicMock,
    queue: CeleryJobQueue,
) -> None:
    mock_to_thread.return_value = "task-123"
    eta = datetime.now(UTC) + timedelta(hours=1)

    result = await queue.enqueue(JobName.SEND_REMINDER, 42, eta=eta)

    assert result == "task-123"
    mock_to_thread.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.workers.queue.asyncio.to_thread")
async def test_enqueue_sanitizes_email_args(
    mock_to_thread: MagicMock,
    queue: CeleryJobQueue,
) -> None:
    mock_to_thread.return_value = "task-email"

    result = await queue.enqueue(
        JobName.SEND_RESET_EMAIL,
        "  user@glorng.dev  ",
        " reset-token ",
    )

    assert result == "task-email"
    mock_to_thread.assert_awaited_once()
