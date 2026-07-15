"""Unit tests for Redis startup connectivity checks."""

from unittest.mock import AsyncMock, patch

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.redis import close_redis, init_redis


@pytest.mark.asyncio
async def test_init_redis_pings_on_startup() -> None:
    """init_redis should verify connectivity with ping before binding the client."""
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    with patch("app.core.redis.Redis.from_url", return_value=mock_client) as from_url:
        await init_redis("redis://:pass@redis:6379/0")
    from_url.assert_called_once_with("redis://:pass@redis:6379/0", decode_responses=True)
    mock_client.ping.assert_awaited_once()
    await close_redis()


@pytest.mark.asyncio
async def test_init_redis_raises_when_ping_fails() -> None:
    """init_redis should fail fast and close the client when ping fails."""
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(
        side_effect=RedisConnectionError("Error -2 connecting to redis:6379")
    )
    mock_client.aclose = AsyncMock()
    with (
        patch("app.core.redis.Redis.from_url", return_value=mock_client),
        pytest.raises(RedisConnectionError, match="redis:6379"),
    ):
        await init_redis("redis://:pass@redis:6379/0")
    mock_client.aclose.assert_awaited_once()
    await close_redis()
