"""Feature flag helpers."""

import pytest

from app.core.feature_flags import (
    is_ai_chat_enabled,
    is_ai_search_enabled,
    is_service_enabled,
)
from app.settings import get_settings


def test_ai_chat_disabled_when_flag_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_CHAT_ENABLED", "false")
    get_settings.cache_clear()
    assert is_ai_chat_enabled() is False
    get_settings.cache_clear()


def test_ai_search_requires_flag_and_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_SEARCH_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    assert is_ai_search_enabled() is False
    get_settings.cache_clear()


def test_ai_search_enabled_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_SEARCH_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    get_settings.cache_clear()
    assert is_ai_search_enabled() is True
    get_settings.cache_clear()


def test_service_enabled_respects_ai_chat_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_CHAT_ENABLED", "false")
    get_settings.cache_clear()
    assert is_service_enabled("ai-chat") is False
    assert is_service_enabled("tasks") is True
    get_settings.cache_clear()
