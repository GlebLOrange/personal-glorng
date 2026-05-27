from typing import Any

from redis.asyncio import Redis

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


async def cache_get(key: str) -> str | None:
    return await get_redis_client().get(key)


async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    await get_redis_client().set(key, value, ex=ttl)


async def blacklist_token(jti: str, ttl: int) -> None:
    await get_redis_client().set(f"bl:{jti}", "1", ex=ttl)


async def is_token_blacklisted(jti: str) -> bool:
    result: Any = await get_redis_client().get(f"bl:{jti}")
    return result is not None
