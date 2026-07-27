"""Redis-backed concurrency slots (cross-worker semaphores).

Uses atomic INCR/DECR with a TTL safety net so a crashed worker cannot hold
a slot forever. Prefer this over process-local counters when uvicorn/gunicorn
runs multiple workers.
"""

from redis.exceptions import RedisError

from app.core.logging import logger
from app.core.redis import get_redis_client

# Acquire: reject if at limit, else INCR and refresh TTL.
_ACQUIRE_LUA = """
local limit = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])
local current = tonumber(redis.call('GET', KEYS[1]) or '0')
if current >= limit then
  return 0
end
current = redis.call('INCR', KEYS[1])
redis.call('EXPIRE', KEYS[1], ttl)
return current
"""

# Release: DECR, delete when counter hits zero.
_RELEASE_LUA = """
local current = tonumber(redis.call('GET', KEYS[1]) or '0')
if current <= 1 then
  redis.call('DEL', KEYS[1])
  return 0
end
return redis.call('DECR', KEYS[1])
"""


async def try_acquire_slot(key: str, *, limit: int, ttl: int) -> bool | None:
    """Try to take one slot. True=acquired, False=at capacity, None=Redis error."""
    try:
        client = get_redis_client()
        script = client.register_script(_ACQUIRE_LUA)
        result = int(await script(keys=[key], args=[limit, ttl]))
        return result > 0
    except (RedisError, RuntimeError) as exc:
        logger.warning(
            "Redis slot acquire failed",
            error=exc,
            context={"key": key, "limit": limit},
        )
        return None


async def release_slot(key: str) -> None:
    """Release one slot. Best-effort; TTL is the backstop if this fails."""
    try:
        client = get_redis_client()
        script = client.register_script(_RELEASE_LUA)
        await script(keys=[key], args=[])
    except (RedisError, RuntimeError) as exc:
        logger.warning(
            "Redis slot release failed",
            error=exc,
            context={"key": key},
        )
