"""User Redis cache must not store password hashes."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.core import user_cache
from app.db.documents.user import User


@pytest.mark.asyncio
async def test_set_cached_user_excludes_hashed_password() -> None:
    user = User(
        id=1,
        public_id=uuid.uuid4(),
        email="cache@example.com",
        hashed_password="secret-hash",
        is_verified=True,
    )
    stored: dict[str, str] = {}

    async def fake_set(key: str, value: str, ttl: int = 300) -> None:
        stored["key"] = key
        stored["value"] = value
        stored["ttl"] = str(ttl)

    with patch.object(user_cache, "cache_set", fake_set):
        await user_cache.set_cached_user(user)

    assert "secret-hash" not in stored["value"]
    assert "hashed_password" not in stored["value"]


@pytest.mark.asyncio
async def test_get_cached_user_fills_password_placeholder() -> None:
    public_id = uuid.uuid4()
    raw = (
        f'{{"public_id": "{public_id}", "email": "cache@example.com",'
        f' "is_verified": true, "permissions": []}}'
    )

    with patch.object(user_cache, "cache_get", AsyncMock(return_value=raw)):
        loaded = await user_cache.get_cached_user(public_id)

    assert loaded is not None
    assert loaded.email == "cache@example.com"
    assert loaded.hashed_password == ""
