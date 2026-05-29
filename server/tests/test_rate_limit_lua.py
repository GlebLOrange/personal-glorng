from unittest.mock import MagicMock

import pytest
from fastapi import Request

import app.core.redis as redis_module
from app.core.rate_limit import RateLimiter
from tests.conftest import FakeRedis


@pytest.fixture
def rate_limiter() -> RateLimiter:
    return RateLimiter(requests=2, window=60)


def _make_request(path: str = "/test", ip: str = "127.0.0.1") -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [],
        "client": (ip, 12345),
    }
    return Request(scope)


@pytest.mark.asyncio
async def test_incr_expire_sets_ttl_on_first_hit(
    rate_limiter: RateLimiter,
    fake_redis: FakeRedis,
) -> None:
    request = _make_request()

    await rate_limiter(request)

    assert fake_redis._expiry["rl:/test:127.0.0.1"] == 60


@pytest.mark.asyncio
async def test_incr_expire_does_not_reset_ttl_on_subsequent_hits(
    rate_limiter: RateLimiter,
    fake_redis: FakeRedis,
) -> None:
    request = _make_request()

    await rate_limiter(request)
    fake_redis._expiry["rl:/test:127.0.0.1"] = 30
    await rate_limiter(request)

    assert fake_redis._expiry["rl:/test:127.0.0.1"] == 30


@pytest.mark.asyncio
async def test_uses_lua_script_via_register_script(
    rate_limiter: RateLimiter,
    fake_redis: FakeRedis,
) -> None:
    fake_redis.register_script = MagicMock(wraps=fake_redis.register_script)
    redis_module._redis = fake_redis

    await rate_limiter(_make_request())

    fake_redis.register_script.assert_called_once()
