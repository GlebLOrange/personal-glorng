from typing import Any
from urllib.parse import urlparse

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.logging import logger
from app.core.redis_keys import BLACKLIST_PREFIX
from app.settings import get_settings

_redis: Redis | None = None
_redis_cache: Redis | None = None

# Cap pool size so multi-worker API processes cannot unbounded-open connections.
_MAX_CONNECTIONS = 50


def _redis_endpoint(url: str) -> str:
    """Return host:port for logs without credentials."""
    parsed = urlparse(url)
    host = parsed.hostname or "unknown"
    port = parsed.port or 6379
    return f"{host}:{port}"


async def _connect_redis(url: str, *, label: str) -> Redis:
    client = Redis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        max_connections=_MAX_CONNECTIONS,
    )
    endpoint = _redis_endpoint(url)
    try:
        await client.ping()
    except RedisError as exc:
        await client.aclose()
        logger.error(
            "Redis connection failed at startup",
            error=exc,
            context={"endpoint": endpoint, "role": label},
        )
        raise
    logger.info(
        "Redis connected",
        context={"endpoint": endpoint, "role": label},
    )
    return client


async def init_redis(url: str, cache_url: str | None = None) -> None:
    """Initialize security Redis and optional cache Redis before accepting traffic.

    When ``cache_url`` is empty or equals ``url``, cache helpers share the security
    client. Production should point ``REDIS_CACHE_URL`` at a separate Redis with
    ``allkeys-lru`` so cache pressure cannot block blacklist or rate-limit writes
    on the ``noeviction`` security instance.
    """
    global _redis, _redis_cache
    _redis = await _connect_redis(url, label="security")
    resolved_cache = (cache_url or "").strip() or url
    if resolved_cache == url:
        _redis_cache = _redis
    else:
        _redis_cache = await _connect_redis(resolved_cache, label="cache")


async def close_redis() -> None:
    global _redis, _redis_cache
    cache = _redis_cache
    security = _redis
    _redis_cache = None
    _redis = None
    if cache is not None and cache is not security:
        await cache.aclose()
    if security is not None:
        await security.aclose()


def get_redis_client() -> Redis:
    """Return the security Redis client (blacklist, rate limits, OAuth, locks)."""
    if _redis is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis


def get_redis_cache_client() -> Redis:
    """Return the cache Redis client (may share the security client)."""
    if _redis_cache is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_cache


async def get_redis_memory_info() -> dict[str, Any]:
    """Return Redis memory stats for readiness probes (security instance)."""
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
        return await get_redis_cache_client().get(key)
    except RedisError as exc:
        logger.warning("Redis cache_get failed", error=exc, context={"key": key})
        return None


async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    try:
        await get_redis_cache_client().set(key, value, ex=ttl)
    except RedisError as exc:
        logger.warning("Redis cache_set failed", error=exc, context={"key": key})


async def cache_set_nx(key: str, value: str, ttl: int) -> bool | None:
    """Set key only if absent on the security Redis (locks / idempotency).

    Returns True if set, False if existed, None on Redis error.
    """
    try:
        client = get_redis_client()
        try:
            return bool(await client.set(key, value, ex=ttl, nx=True))
        except TypeError:
            # ponytail: FakeRedis in tests lacks nx=; race-y fallback is fine there.
            existing = await client.get(key)
            if existing is not None:
                return False
            await client.set(key, value, ex=ttl)
            return True
    except (RedisError, RuntimeError) as exc:
        logger.warning("Redis cache_set_nx failed", error=exc, context={"key": key})
        return None


async def cache_delete(key: str) -> None:
    try:
        await get_redis_cache_client().delete(key)
    except (RedisError, RuntimeError) as exc:
        logger.warning("Redis cache_delete failed", error=exc, context={"key": key})


async def cache_getdel(key: str) -> str | None:
    """Atomically get and delete a security key (one-time OAuth consume)."""
    try:
        result: Any = await get_redis_client().getdel(key)
        return result
    except RedisError as exc:
        logger.warning("Redis cache_getdel failed", error=exc, context={"key": key})
        return None


async def security_set(key: str, value: str, ttl: int) -> None:
    """Set a security-critical key on the noeviction Redis (OAuth state, etc.)."""
    await get_redis_client().set(key, value, ex=ttl)


async def security_delete(key: str) -> None:
    """Delete a security-critical key (locks, OAuth leftovers)."""
    await get_redis_client().delete(key)


async def blacklist_token(jti: str, ttl: int) -> None:
    """Blacklist a JTI (overwrites). Used by logout and forced revoke."""
    # Redis rejects EX 0; skip already-expired tokens.
    if ttl <= 0:
        return
    await get_redis_client().set(f"{BLACKLIST_PREFIX}{jti}", "1", ex=ttl)


async def try_blacklist_token(jti: str, ttl: int) -> bool:
    """Atomically blacklist a JTI. Returns False if it was already blacklisted."""
    if ttl <= 0:
        return False
    result = await get_redis_client().set(
        f"{BLACKLIST_PREFIX}{jti}",
        "1",
        ex=ttl,
        nx=True,
    )
    return result is True


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
