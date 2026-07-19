import json
import os
import time
import uuid
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

# Bootstrap: point Settings at the test .env file (must run before app imports).
os.environ["GLORNG_ENV_FILE"] = str(Path(__file__).resolve().parent / ".env.test")

import app.core.redis as redis_module
from app.core.mongodb import bind_mongodb, clear_mongodb
from app.core.security import create_access_token
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.main import app
from app.services.currency import RATES_CACHE_KEY
from app.settings import get_settings
from app.workers.queue import init_job_queue
from tests.env_helpers import BASE_ENV_FILE
from tests.factories import create_user

_TEST_ENV_FILE = str(BASE_ENV_FILE)

USE_SQLITE_TESTS = get_settings().USE_SQLITE_TESTS

ADMIN_EMAIL = "admin@admin.admin"

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
STRONG_PASSWORD = "MyTestPass123!"
ADMIN_PASSWORD = STRONG_PASSWORD

TEST_MONGO_DB = get_settings().MONGODB_DB
_mongo_client = AsyncMongoMockClient()
_mongo_db = _mongo_client[TEST_MONGO_DB]
_test_registry = DatabaseRegistry(mongo_client=_mongo_client, mongo_db=_mongo_db)


class _FakeIncrExpireScript:
    def __init__(self, redis: FakeRedis) -> None:
        self._redis = redis

    async def __call__(self, keys: list[str], args: list[int]) -> int:
        key = keys[0]
        window = int(args[0])
        current = await self._redis.incr(key)
        if current == 1:
            await self._redis.expire(key, window)
        return current


class FakeRedis:
    """Minimal in-memory Redis substitute for tests."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._expiry: dict[str, int] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def getdel(self, key: str) -> str | None:
        value = self._store.pop(key, None)
        self._expiry.pop(key, None)
        return value

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        self._store[key] = str(value)
        if ex is not None:
            self._expiry[key] = ex

    async def incr(self, key: str) -> int:
        val = int(self._store.get(key, "0")) + 1
        self._store[key] = str(val)
        return val

    async def expire(self, key: str, seconds: int) -> None:
        self._expiry[key] = seconds

    def register_script(self, _script: str) -> _FakeIncrExpireScript:
        return _FakeIncrExpireScript(self)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)
        self._expiry.pop(key, None)

    async def ping(self) -> bool:
        return True

    async def info(self, section: str = "default") -> dict[str, Any]:
        return {
            "used_memory": 0,
            "maxmemory": 0,
            "maxmemory_policy": "noeviction",
        }

    async def aclose(self) -> None:
        self._store.clear()
        self._expiry.clear()


async def _ensure_test_mongo_schema(db: Any) -> None:
    """Create MongoDB indexes for tests, skipping text indexes mongomock lacks."""
    from app.db.mongo.indexes import INDEX_SPECS

    _SCHEMA_VERSION = "v001_initial_indexes"
    for collection, keys, options in INDEX_SPECS:
        if any(len(key) == 2 and key[1] == "text" for key in keys):
            continue
        kwargs = options or {}
        await db[collection].create_index(keys, **kwargs)
    await db.schema_migrations.update_one(
        {"_id": _SCHEMA_VERSION},
        {"$set": {"applied": True}},
        upsert=True,
    )


async def _drop_all_collections() -> None:
    for name in await _mongo_db.list_collection_names():
        await _mongo_db[name].delete_many({})


if USE_SQLITE_TESTS:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    TEST_DB_URL = "sqlite+aiosqlite:///./test.db"
    _pg_engine = create_async_engine(TEST_DB_URL, echo=False)
    _pg_session_factory = async_sessionmaker(
        _pg_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture(autouse=True)
def mongomock_compat(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    """Adapt repository serialization and search for mongomock limitations."""
    import app.db.repositories.base as repo_base
    from app.db.repositories.search import SearchRepository
    from app.db.repositories.user import UserRepository

    original_to_dict = repo_base.document_to_dict

    def _mongomock_safe_to_dict(
        doc: Any, *, exclude_none: bool = False
    ) -> dict[str, Any]:
        data = original_to_dict(doc, exclude_none=exclude_none)
        safe: dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, uuid.UUID) or isinstance(value, Decimal):
                safe[key] = str(value)
            elif isinstance(value, datetime):
                safe[key] = value
            elif isinstance(value, date) and not isinstance(value, datetime):
                safe[key] = datetime.combine(value, datetime.min.time(), tzinfo=UTC)
            else:
                safe[key] = value
        return safe

    async def _search_text_regex(
        self: SearchRepository,
        query: str,
        *,
        limit: int = 6,
        visibility: str | None = None,
    ) -> list[Any]:
        mongo_query: dict[str, Any] = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"body": {"$regex": query, "$options": "i"}},
            ],
        }
        if visibility:
            mongo_query = {"$and": [mongo_query, {"visibility": visibility}]}
        cursor = self._col().find(mongo_query).limit(limit)
        from app.db.documents.search import SearchDocument

        return [repo_base._parse_doc(SearchDocument, row) async for row in cursor]

    async def _get_user_by_public_id_str(
        self: UserRepository,
        public_id: str | uuid.UUID,
    ) -> User | None:
        try:
            uid = (
                public_id
                if isinstance(public_id, uuid.UUID)
                else uuid.UUID(str(public_id))
            )
        except ValueError:
            return None
        data = await self._col().find_one({"public_id": str(uid)})
        if data is None:
            return None
        return repo_base._parse_doc(User, data)

    def _serialize_field(value: Any) -> Any:
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, date) and not isinstance(value, datetime):
            return datetime.combine(value, datetime.min.time(), tzinfo=UTC)
        return value

    original_update_fields = repo_base.MongoRepository.update_fields

    async def _mongomock_update_fields(
        self: repo_base.MongoRepository,
        doc_id: int,
        **fields: Any,
    ) -> Any:
        safe_fields = {key: _serialize_field(value) for key, value in fields.items()}
        return await original_update_fields(self, doc_id, **safe_fields)

    monkeypatch.setattr(repo_base, "document_to_dict", _mongomock_safe_to_dict)
    monkeypatch.setattr(
        repo_base.MongoRepository,
        "update_fields",
        _mongomock_update_fields,
    )
    monkeypatch.setattr(SearchRepository, "search_text", _search_text_regex)
    monkeypatch.setattr(
        UserRepository,
        "get_by_public_id",
        _get_user_by_public_id_str,
    )
    return


@pytest.fixture(autouse=True)
def _reset_settings_env(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    monkeypatch.setenv("GLORNG_ENV_FILE", _TEST_ENV_FILE)
    get_settings.cache_clear()
    yield
    monkeypatch.setenv("GLORNG_ENV_FILE", _TEST_ENV_FILE)
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
async def setup_mongo_registry() -> AsyncGenerator[None]:
    get_settings.cache_clear()
    await _ensure_test_mongo_schema(_mongo_db)
    _test_registry.init_repositories()
    app.state.db_registry = _test_registry
    bind_mongodb(_mongo_client, _mongo_db)
    yield
    await _drop_all_collections()
    clear_mongodb()


@pytest.fixture(autouse=True)
def reset_worker_registry() -> Generator[None]:
    import app.db.worker_registry as worker_registry_module

    worker_registry_module._registry = None
    yield
    worker_registry_module._registry = None


@pytest.fixture(autouse=True)
def fake_redis(request: pytest.FixtureRequest) -> Generator[FakeRedis | None]:
    if request.node.get_closest_marker("redis"):
        yield None
        return
    fake = FakeRedis()
    redis_module._redis = fake  # type: ignore[assignment]
    yield fake


@pytest.fixture(autouse=True)
async def seed_currency_rates(fake_redis: FakeRedis | None) -> None:
    if fake_redis is None:
        return
    await fake_redis.set(RATES_CACHE_KEY, json.dumps(TEST_RATES_PAYLOAD))


@pytest.fixture(autouse=True)
def temp_media_dir(tmp_path: Path) -> Generator[None]:
    settings = get_settings()
    original = settings.MEDIA_DIR
    settings.MEDIA_DIR = str(tmp_path / "media")
    yield
    settings.MEDIA_DIR = original


init_job_queue()


@pytest.fixture
def registry() -> DatabaseRegistry:
    return _test_registry


@pytest.fixture
def db(registry: DatabaseRegistry) -> DatabaseRegistry:
    """Alias for registry (backward-compatible fixture name)."""
    return registry


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def admin_user(registry: DatabaseRegistry) -> User:
    return await create_user(
        registry,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
        is_protected=True,
    )


@pytest.fixture
def admin_token(admin_user: User) -> str:
    return create_access_token(str(admin_user.public_id), user_id=admin_user.id)


@pytest.fixture
async def auth_client(
    client: AsyncClient, admin_token: str
) -> AsyncGenerator[AsyncClient]:
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
