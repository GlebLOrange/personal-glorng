from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.core.mongodb import (
    bind_mongodb,
    clear_mongodb,
    get_mongodb_client,
    get_mongodb_database,
    is_mongodb_enabled,
)
from app.settings import get_settings
from tests.env_helpers import activate_env_file, scenario_env


@pytest.fixture(autouse=True)
def _reset_mongodb_module() -> None:
    yield
    clear_mongodb()


def test_bind_mongodb_registers_client_and_database() -> None:
    mock_client = MagicMock()
    mock_db = MagicMock()

    bind_mongodb(mock_client, mock_db)

    assert is_mongodb_enabled()
    assert get_mongodb_client() is mock_client
    assert get_mongodb_database() is mock_db


def test_clear_mongodb_unregisters_helpers() -> None:
    mock_client = MagicMock()
    mock_db = MagicMock()
    bind_mongodb(mock_client, mock_db)

    clear_mongodb()

    assert not is_mongodb_enabled()


def test_resolve_mongodb_url_maps_compose_host_to_localhost(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(
            tmp_path,
            MONGODB_URL="mongodb://user:pass@mongodb:27017/glorng?authSource=admin",
            MONGODB_USER="user",
            MONGODB_PASSWORD="pass",
            MONGODB_DB="glorng",
        ),
    )

    settings = get_settings()
    assert settings.MONGODB_URL == (
        "mongodb://user:pass@127.0.0.1:27017/glorng?authSource=admin"
    )

    get_settings.cache_clear()
