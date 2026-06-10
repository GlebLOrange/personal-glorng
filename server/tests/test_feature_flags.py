"""Feature flag helpers."""

from pathlib import Path

import pytest

from app.core.feature_flags import (
    is_ai_chat_enabled,
    is_ai_search_enabled,
    is_service_enabled,
)
from app.settings import get_settings
from tests.env_helpers import activate_env_file, scenario_env


def test_ai_chat_disabled_when_flag_off(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(monkeypatch, scenario_env(tmp_path, AI_CHAT_ENABLED="false"))
    assert is_ai_chat_enabled() is False
    get_settings.cache_clear()


def test_ai_search_requires_flag_and_api_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(tmp_path, AI_SEARCH_ENABLED="true", OPENAI_API_KEY=""),
    )
    assert is_ai_search_enabled() is False
    get_settings.cache_clear()


def test_ai_search_enabled_with_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(tmp_path, AI_SEARCH_ENABLED="true", OPENAI_API_KEY="sk-test-key"),
    )
    assert is_ai_search_enabled() is True
    get_settings.cache_clear()


def test_service_enabled_respects_ai_chat_flag(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(monkeypatch, scenario_env(tmp_path, AI_CHAT_ENABLED="false"))
    assert is_service_enabled("ai-chat") is False
    assert is_service_enabled("tasks") is True
    get_settings.cache_clear()
