"""Unit tests for Redis concurrency slots (vid-download cross-worker semaphores)."""

from unittest.mock import patch

import pytest
from redis.exceptions import RedisError

import app.core.redis as redis_module
from app.core.exceptions import ApiError
from app.core.redis_keys import VID_DOWNLOAD_GLOBAL_KEY, VID_DOWNLOAD_IP_PREFIX
from app.core.redis_slots import release_slot, try_acquire_slot
from app.routers.tools.viddownload import (
    _SLOT_TTL_SEC,
    MAX_CONCURRENT_DOWNLOADS,
    MAX_CONCURRENT_PER_IP,
    _acquire_global_slot,
    _acquire_ip_slot,
    _release_global_slot,
    _release_ip_slot,
)
from tests.conftest import FakeRedis


@pytest.mark.asyncio
async def test_try_acquire_slot_respects_limit(fake_redis: FakeRedis) -> None:
    redis_module._redis = fake_redis
    key = "slot:test"

    assert await try_acquire_slot(key, limit=2, ttl=60) is True
    assert await try_acquire_slot(key, limit=2, ttl=60) is True
    assert await try_acquire_slot(key, limit=2, ttl=60) is False
    assert fake_redis._store[key] == "2"


@pytest.mark.asyncio
async def test_release_slot_decrements_and_deletes(fake_redis: FakeRedis) -> None:
    redis_module._redis = fake_redis
    key = "slot:release"

    assert await try_acquire_slot(key, limit=2, ttl=60) is True
    assert await try_acquire_slot(key, limit=2, ttl=60) is True
    await release_slot(key)
    assert fake_redis._store[key] == "1"
    await release_slot(key)
    assert key not in fake_redis._store


@pytest.mark.asyncio
async def test_try_acquire_slot_returns_none_on_redis_error(
    fake_redis: FakeRedis,
) -> None:
    redis_module._redis = fake_redis

    with patch.object(fake_redis, "register_script", side_effect=RedisError("boom")):
        assert await try_acquire_slot("slot:err", limit=1, ttl=60) is None


@pytest.mark.asyncio
async def test_viddownload_global_slot_limit(fake_redis: FakeRedis) -> None:
    redis_module._redis = fake_redis

    await _acquire_global_slot()
    await _acquire_global_slot()
    with pytest.raises(ApiError) as exc_info:
        await _acquire_global_slot()
    assert exc_info.value.status_code == 503
    assert fake_redis._store[VID_DOWNLOAD_GLOBAL_KEY] == str(MAX_CONCURRENT_DOWNLOADS)

    await _release_global_slot()
    await _acquire_global_slot()  # frees one, then re-acquire ok


@pytest.mark.asyncio
async def test_viddownload_ip_slot_limit(fake_redis: FakeRedis) -> None:
    redis_module._redis = fake_redis
    ip = "203.0.113.9"

    await _acquire_ip_slot(ip)
    with pytest.raises(ApiError) as exc_info:
        await _acquire_ip_slot(ip)
    assert exc_info.value.status_code == 503
    assert fake_redis._store[f"{VID_DOWNLOAD_IP_PREFIX}{ip}"] == str(
        MAX_CONCURRENT_PER_IP
    )

    await _release_ip_slot(ip)
    await _acquire_ip_slot(ip)


@pytest.mark.asyncio
async def test_viddownload_slots_fail_closed_on_redis_error(
    fake_redis: FakeRedis,
) -> None:
    redis_module._redis = fake_redis

    with (
        patch(
            "app.routers.tools.viddownload.try_acquire_slot",
            return_value=None,
        ),
        pytest.raises(ApiError) as exc_info,
    ):
        await _acquire_global_slot()
    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_acquire_sets_ttl_safety_net(fake_redis: FakeRedis) -> None:
    redis_module._redis = fake_redis

    await _acquire_global_slot()
    deadline = fake_redis._expiry[VID_DOWNLOAD_GLOBAL_KEY]
    import time

    remaining = deadline - time.monotonic()
    assert _SLOT_TTL_SEC - 1.0 <= remaining <= _SLOT_TTL_SEC + 1.0
