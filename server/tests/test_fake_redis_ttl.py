"""Spot-check FakeRedis TTL behaviour used by the P0 suite."""

import time

import pytest

from tests.conftest import FakeRedis


@pytest.mark.asyncio
async def test_fake_redis_honours_ttl() -> None:
    redis = FakeRedis()
    await redis.set("k", "v", ex=1)
    assert await redis.get("k") == "v"
    time.sleep(1.05)
    assert await redis.get("k") is None


@pytest.mark.asyncio
async def test_fake_redis_expire_sets_deadline() -> None:
    redis = FakeRedis()
    await redis.set("k", "v")
    await redis.expire("k", 1)
    assert await redis.get("k") == "v"
    time.sleep(1.05)
    assert await redis.get("k") is None
