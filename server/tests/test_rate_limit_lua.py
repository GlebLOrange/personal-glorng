from unittest.mock import MagicMock, patch

import pytest
from fastapi import Request
from redis.exceptions import RedisError

import app.core.redis as redis_module
from app.core.exceptions import ApiError
from app.core.rate_limit import RateLimiter, rate_limit_auth
from app.routers.donations import rate_limit_checkout
from app.routers.feedback import rate_limit_feedback
from app.routers.search import rate_limit_search_chat
from app.routers.tools.ai_chat import rate_limit_ai_chat
from app.routers.tools.urlshortener import rate_limit_shortener_create
from app.routers.tools.viddownload import rate_limit_vid_download
from app.routers.webhooks import rate_limit_webhook
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


@pytest.mark.asyncio
async def test_fail_open_allows_request_when_redis_unavailable() -> None:
    limiter = RateLimiter(requests=2, window=60, fail_open=True)
    with patch(
        "app.core.rate_limit.get_redis_client",
        side_effect=RedisError("connection refused"),
    ):
        await limiter(_make_request())


@pytest.mark.asyncio
async def test_fail_closed_rejects_request_when_redis_unavailable() -> None:
    limiter = RateLimiter(requests=2, window=60, fail_open=False)
    with (
        patch(
            "app.core.rate_limit.get_redis_client",
            side_effect=RedisError("connection refused"),
        ),
        pytest.raises(ApiError) as exc_info,
    ):
        await limiter(_make_request())

    assert exc_info.value.status_code == 503


def test_auth_rate_limiter_is_fail_closed() -> None:
    assert rate_limit_auth.fail_open is False


def test_abuse_sensitive_public_limiters_are_fail_closed() -> None:
    assert rate_limit_feedback.fail_open is False
    assert rate_limit_checkout.fail_open is False
    assert rate_limit_ai_chat.fail_open is False
    assert rate_limit_search_chat.fail_open is False
    assert rate_limit_shortener_create.fail_open is False
    assert rate_limit_vid_download.fail_open is False
    assert rate_limit_webhook.fail_open is False
