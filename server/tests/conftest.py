import json
import time
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.core.redis as redis_module
from app.core.database import get_db
from app.core.security import create_access_token
from app.main import app
from app.models.base import Base
from app.models.user import User
from app.settings import get_settings
from app.services.currency import RATES_CACHE_KEY
from tests.factories import create_user

ADMIN_EMAIL = "admin@glorng.dev"

TEST_RATES_PAYLOAD = {
    "result": "success",
    "base_code": "USD",
    "time_last_update_utc": "Wed, 27 May 2026 00:00:00 +0000",
    "time_next_update_unix": int(time.time()) + 86400,
    "rates": {
        "USD": 1,
        "EUR": 0.86,
        "PLN": 3.64,
        "BYN": 2.76,
    },
}
ADMIN_PASSWORD = "testpass123"


class FakeRedis:
    """Minimal in-memory Redis substitute for tests."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        self._store[key] = str(value)

    async def incr(self, key: str) -> int:
        val = int(self._store.get(key, "0")) + 1
        self._store[key] = str(val)
        return val

    async def expire(self, key: str, seconds: int) -> None:
        pass

    async def aclose(self) -> None:
        self._store.clear()


TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DB_URL, echo=False)
test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def fake_redis() -> FakeRedis:
    fake = FakeRedis()
    redis_module._redis = fake  # type: ignore[assignment]
    return fake


@pytest.fixture(autouse=True)
async def seed_currency_rates(fake_redis: FakeRedis) -> None:
    await fake_redis.set(RATES_CACHE_KEY, json.dumps(TEST_RATES_PAYLOAD))


@pytest.fixture(autouse=True)
def temp_media_dir(tmp_path: Path) -> Generator[None, None, None]:
    settings = get_settings()
    original = settings.MEDIA_DIR
    settings.MEDIA_DIR = str(tmp_path / "media")
    yield
    settings.MEDIA_DIR = original


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session() as session:
        yield session


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    return await create_user(
        db, email=ADMIN_EMAIL, password=ADMIN_PASSWORD, is_admin=True
    )


@pytest.fixture
def admin_token(admin_user: User) -> str:
    return create_access_token(str(admin_user.id))


@pytest.fixture
async def auth_client(
    client: AsyncClient, admin_token: str
) -> AsyncGenerator[AsyncClient, None]:
    client.headers["Authorization"] = f"Bearer {admin_token}"
    return client


@pytest.fixture
async def login_tokens(client: AsyncClient, admin_user: User) -> dict[str, str]:
    resp = await client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200
    return resp.json()
