"""Short-TTL Redis cache for authenticated user lookups."""

from __future__ import annotations

import uuid

from app.core.cache_json import safe_cache_json_loads
from app.core.redis import cache_delete, cache_get, cache_set
from app.core.redis_keys import USER_CACHE_PREFIX
from app.db.documents.user import User

USER_CACHE_TTL_SECONDS = 45


def _cache_key(public_id: str | uuid.UUID) -> str:
    return f"{USER_CACHE_PREFIX}{public_id}"


async def get_cached_user(public_id: str | uuid.UUID) -> User | None:
    raw = await cache_get(_cache_key(public_id))
    if raw is None:
        return None
    payload = safe_cache_json_loads(raw)
    if not isinstance(payload, dict):
        return None
    try:
        return User.model_validate(payload)
    except (TypeError, ValueError):
        return None


async def set_cached_user(user: User) -> None:
    await cache_set(
        _cache_key(user.public_id),
        user.model_dump_json(),
        ttl=USER_CACHE_TTL_SECONDS,
    )


async def invalidate_user_cache(public_id: str | uuid.UUID) -> None:
    await cache_delete(_cache_key(public_id))
