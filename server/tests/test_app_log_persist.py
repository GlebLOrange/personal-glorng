import asyncio

import pytest

from app.core.app_log_persist import (
    _drain_queue,
    enqueue_log_entry,
    start_app_log_worker,
    stop_app_log_worker,
)
from app.db.documents.app_log import AppLog
from app.db.registry import DatabaseRegistry
from app.settings import get_settings


def _sample_entry(*, level: str = "info", path: str | None = None) -> dict:
    entry = {
        "timestamp": "2026-06-07T12:00:00",
        "level": level,
        "message": "Test log message",
        "logger": "glorng",
        "request_id": "req-123",
    }
    if path is not None:
        entry["path"] = path
    return entry


def test_enqueue_skips_health_probe() -> None:
    _drain_queue()
    enqueue_log_entry(_sample_entry(path="/api/health"))
    assert _drain_queue() == []


def test_enqueue_respects_min_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_LOG_PERSIST_MIN_LEVEL", "WARNING")
    get_settings.cache_clear()

    before = len(_drain_queue())
    enqueue_log_entry(_sample_entry(level="info"))
    assert len(_drain_queue()) == before

    enqueue_log_entry(_sample_entry(level="warning"))
    assert len(_drain_queue()) == before + 1

    _drain_queue()
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_worker_persists_batch(registry: DatabaseRegistry) -> None:
    assert registry.app_logs is not None

    await start_app_log_worker()
    try:
        enqueue_log_entry(_sample_entry())
        await asyncio.sleep(1.2)
    finally:
        await stop_app_log_worker()

    items, total = await registry.app_logs.list_events(limit=10)
    assert total >= 1
    assert any(item.message == "Test log message" for item in items)


@pytest.mark.asyncio
async def test_repository_insert_many(registry: DatabaseRegistry) -> None:
    assert registry.app_logs is not None
    await registry.app_logs.insert_many(
        [
            AppLog(id=0, level="info", message="Persisted", logger="test"),
            AppLog(id=0, level="error", message="Failed", logger="test"),
        ],
    )

    items, total = await registry.app_logs.list_events(level="error")
    assert total == 1
    assert items[0].message == "Failed"
