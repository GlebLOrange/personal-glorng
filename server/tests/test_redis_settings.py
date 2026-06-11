from pathlib import Path

import pytest

from app.settings import get_settings
from tests.env_helpers import activate_env_file, scenario_env


def test_resolve_redis_url_maps_compose_host_to_localhost(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(
            tmp_path,
            REDIS_URL="redis://:pass@redis:6379/0",
        ),
    )

    settings = get_settings()
    assert settings.REDIS_URL == "redis://:pass@127.0.0.1:6379/0"

    get_settings.cache_clear()
