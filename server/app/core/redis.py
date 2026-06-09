from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.logging import logger
from app.core.redis_keys import BLACKLIST_PREFIX
from app.settings import get_settings

_redis: Redis | None = None


async def init_redis(url: str) -> None:
    global _redis
    _redis = Redis.from_url(url, decode_responses=True)


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


def get_redis_client() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis


async def get_redis_memory_info() -> dict[str, Any]:
    """Return Redis memory stats for readiness probes."""
    client = get_redis_client()
    info = await client.info("memory")
    used = int(info.get("used_memory", 0))
    maxmemory = int(info.get("maxmemory", 0))
    policy = str(info.get("maxmemory_policy", "unknown"))
    payload: dict[str, Any] = {
        "used_memory": used,
        "maxmemory": maxmemory,
        "maxmemory_policy": policy,
    }
    if maxmemory > 0 and used > maxmemory * 0.85:
        payload["warning"] = "memory_above_85_percent"
    return payload


async def cache_get(key: str) -> str | None:
    try:
        return await get_redis_client().get(key)
    except RedisError as exc:
        logger.warning("Redis cache_get failed", error=exc, context={"key": key})
        return None


async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    try:
        await get_redis_client().set(key, value, ex=ttl)
    except RedisError as exc:
        logger.warning("Redis cache_set failed", error=exc, context={"key": key})


async def cache_delete(key: str) -> None:
    try:
        await get_redis_client().delete(key)
    except RedisError as exc:
        logger.warning("Redis cache_delete failed", error=exc, context={"key": key})


async def blacklist_token(jti: str, ttl: int) -> None:
    await get_redis_client().set(f"{BLACKLIST_PREFIX}{jti}", "1", ex=ttl)


async def is_token_blacklisted(jti: str) -> bool:
    """Return True when token is revoked; fail-closed in production on Redis errors."""
    try:
        result: Any = await get_redis_client().get(f"{BLACKLIST_PREFIX}{jti}")
        return result is not None
    except RedisError as exc:
        settings = get_settings()
        fail_closed = settings.APP_ENV == "production"
        logger.warning(
            "Redis blacklist check failed",
            error=exc,
            context={"jti": jti, "fail_closed": fail_closed},
        )
        return fail_closed
