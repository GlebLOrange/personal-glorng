"""Redis-backed fixed-window rate limiter."""

from fastapi import Request

from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.redis import get_redis_client

_INCR_EXPIRE_LUA = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""


class RateLimiter:
    def __init__(self, requests: int = 10, window: int = 60) -> None:
        self.requests = requests
        self.window = window

    async def __call__(self, request: Request) -> None:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        key = f"rl:{request.url.path}:{client_ip}"
        redis = get_redis_client()
        script = redis.register_script(_INCR_EXPIRE_LUA)
        current = int(await script(keys=[key], args=[self.window]))

        if current > self.requests:
            logger.warning(
                "Rate limit exceeded",
                context={
                    "ip": client_ip,
                    "path": str(request.url.path),
                    "count": current,
                    "limit": self.requests,
                },
            )
            raise ApiError(429, "Too many requests. Please try again later.")


rate_limit_auth = RateLimiter(requests=5, window=60)
rate_limit_api = RateLimiter(requests=30, window=60)
rate_limit_shortener_create = RateLimiter(requests=10, window=3600)
rate_limit_vid_download = RateLimiter(requests=5, window=3600)
