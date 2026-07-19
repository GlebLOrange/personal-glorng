"""Redis-backed fixed-window rate limiter."""

from fastapi import Request
from redis.exceptions import RedisError

from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.redis import get_redis_client
from app.core.redis_keys import RATE_LIMIT_PREFIX


def client_ip(request: Request) -> str:
    """Prefer nginx-set X-Real-IP; avoid spoofable X-Forwarded-For in dev-lite."""
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client:
        return request.client.host
    return "unknown"


_INCR_EXPIRE_LUA = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""


class RateLimiter:
    def __init__(
        self,
        requests: int = 10,
        window: int = 60,
        *,
        fail_open: bool = True,
    ) -> None:
        self.requests = requests
        self.window = window
        self.fail_open = fail_open

    async def __call__(self, request: Request) -> None:
        client_addr = client_ip(request)
        key = f"{RATE_LIMIT_PREFIX}{request.url.path}:{client_addr}"
        try:
            redis = get_redis_client()
            script = redis.register_script(_INCR_EXPIRE_LUA)
            current = int(await script(keys=[key], args=[self.window]))
        except RedisError as exc:
            if not self.fail_open:
                logger.warning(
                    "Rate limit check failed; rejecting request",
                    context={
                        "path": str(request.url.path),
                        "ip": client_addr,
                        "error": str(exc),
                    },
                )
                raise ApiError(503, "Service temporarily unavailable") from exc
            logger.warning(
                "Rate limit check failed; allowing request",
                context={
                    "path": str(request.url.path),
                    "ip": client_addr,
                    "error": str(exc),
                },
            )
            return

        if current > self.requests:
            logger.warning(
                "Rate limit exceeded",
                context={
                    "ip": client_addr,
                    "path": str(request.url.path),
                    "count": current,
                    "limit": self.requests,
                },
            )
            raise ApiError(429, "Too many requests. Please try again later.")


rate_limit_auth = RateLimiter(requests=5, window=60, fail_open=False)
rate_limit_api = RateLimiter(requests=30, window=60)
rate_limit_shortener_create = RateLimiter(requests=10, window=3600, fail_open=False)
rate_limit_vid_download = RateLimiter(requests=5, window=3600, fail_open=False)
rate_limit_admin = RateLimiter(requests=60, window=60, fail_open=False)
rate_limit_email_tool = RateLimiter(requests=10, window=60, fail_open=False)
