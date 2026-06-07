from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.mongodb import (
    close_mongodb,
    get_mongodb_client,
    get_mongodb_database,
    init_mongodb,
    is_mongodb_enabled,
)
from app.settings import get_settings


@pytest.fixture(autouse=True)
def _reset_mongodb_module() -> None:
    yield
    import app.core.mongodb as mongodb_module

    mongodb_module._client = None
    mongodb_module._database = None
    mongodb_module._enabled = False


async def test_init_mongodb_skips_empty_url() -> None:
    await init_mongodb("", "glorng")
    assert not is_mongodb_enabled()


async def test_init_mongodb_connects_and_pings() -> None:
    mock_client = MagicMock()
    mock_client.admin.command = AsyncMock(return_value={"ok": 1})
    mock_db = MagicMock()

    with patch(
        "app.core.mongodb.AsyncIOMotorClient",
        return_value=mock_client,
    ) as client_ctor:
        mock_client.__getitem__.return_value = mock_db
        await init_mongodb("mongodb://localhost:27017/glorng", "glorng")

    client_ctor.assert_called_once_with("mongodb://localhost:27017/glorng")
    mock_client.admin.command.assert_awaited_once_with("ping")
    mock_client.__getitem__.assert_called_once_with("glorng")
    assert is_mongodb_enabled()
    assert get_mongodb_client() is mock_client
    assert get_mongodb_database() is mock_db

    await close_mongodb()
    mock_client.close.assert_called_once()
    assert not is_mongodb_enabled()


def test_resolve_mongodb_url_maps_compose_host_to_localhost(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "MONGODB_URL",
        "mongodb://user:pass@mongodb:27017/glorng?authSource=admin",
    )
    monkeypatch.setenv("MONGODB_USER", "user")
    monkeypatch.setenv("MONGODB_PASSWORD", "pass")
    monkeypatch.setenv("MONGODB_DB", "glorng")
    get_settings.cache_clear()

    settings = get_settings()
    assert settings.MONGODB_URL == (
        "mongodb://user:pass@127.0.0.1:27017/glorng?authSource=admin"
    )

    get_settings.cache_clear()
