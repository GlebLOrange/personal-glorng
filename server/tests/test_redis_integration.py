"""Real Redis integration tests (P1 nightly tier)."""

import pytest

from app.core.redis import close_redis, get_redis_client, init_redis
from app.settings import get_settings


@pytest.mark.redis
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_redis_ping() -> None:
    redis_url = get_settings().REDIS_URL
    if not redis_url or ("127.0.0.1" not in redis_url and "localhost" not in redis_url):
        pytest.skip("REDIS_URL must point at a test Redis instance")

    await init_redis(redis_url)
    try:
        assert await get_redis_client().ping() is True
    finally:
        await close_redis()
    get_settings.cache_clear()


@pytest.mark.redis
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_redis_set_get_roundtrip() -> None:
    redis_url = get_settings().REDIS_URL
    if not redis_url:
        pytest.skip("REDIS_URL not set")

    await init_redis(redis_url)
    try:
        client = get_redis_client()
        await client.set("glorng:test:key", "value", ex=60)
        assert await client.get("glorng:test:key") == "value"
        await client.delete("glorng:test:key")
    finally:
        await close_redis()
