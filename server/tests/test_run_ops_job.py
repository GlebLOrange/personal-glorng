"""Tests for hand-run ops job CLI (sync / cleanup)."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

from app.scripts.run_ops_job import main, run_job

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_run_job_rejects_unknown() -> None:
    """Unknown job names exit with usage text."""
    with pytest.raises(SystemExit, match="Usage"):
        run_job("not-a-job")


def test_main_requires_exactly_one_arg(monkeypatch: MonkeyPatch) -> None:
    """CLI requires a single job name."""
    monkeypatch.setattr("sys.argv", ["run_ops_job"])
    with pytest.raises(SystemExit, match="Usage"):
        main()


def test_run_job_sync_calls_process_sync_queue() -> None:
    """sync runs process_sync_queue via run_async."""
    mock_sync = AsyncMock()
    with (
        patch("app.scripts.run_ops_job.process_sync_queue", mock_sync),
        patch("app.scripts.run_ops_job.run_async") as run_async_mock,
    ):
        run_job("sync")
        mock_sync.assert_called_once_with()
        run_async_mock.assert_called_once()


def test_run_job_cleanup_runs_all_cleanups() -> None:
    """cleanup runs old tasks, expired shares, and health results."""
    mock_old = AsyncMock()
    mock_shares = AsyncMock()
    mock_health = AsyncMock()
    with (
        patch("app.scripts.run_ops_job.cleanup_old_tasks", mock_old),
        patch("app.scripts.run_ops_job.cleanup_expired_shares", mock_shares),
        patch("app.scripts.run_ops_job.cleanup_health_results", mock_health),
        patch("app.scripts.run_ops_job.run_async") as run_async_mock,
    ):
        run_job("cleanup")
        run_async_mock.assert_called_once()
        # Drive the coroutine passed to run_async so Awaitables are awaited.
        # ponytail: asyncio.run is fine in a sync test for one short cleanup chain
        asyncio.run(run_async_mock.call_args.args[0])
        mock_old.assert_awaited_once()
        mock_shares.assert_awaited_once()
        mock_health.assert_awaited_once()
