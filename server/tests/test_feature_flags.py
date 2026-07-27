"""Feature flag helpers."""

from pathlib import Path

import pytest
from httpx import AsyncClient

from app.core.feature_flags import (
    is_ai_chat_enabled,
    is_ai_search_enabled,
    is_expenses_enabled,
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


def test_ai_chat_requires_flag_and_api_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(tmp_path, AI_CHAT_ENABLED="true", GROQ_API_KEY=""),
    )
    assert is_ai_chat_enabled() is False
    get_settings.cache_clear()


def test_ai_chat_enabled_with_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(tmp_path, AI_CHAT_ENABLED="true", GROQ_API_KEY="sk-test-key"),
    )
    assert is_ai_chat_enabled() is True
    get_settings.cache_clear()


def test_ai_search_requires_flag_and_api_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(tmp_path, AI_SEARCH_ENABLED="true", GROQ_API_KEY=""),
    )
    assert is_ai_search_enabled() is False
    get_settings.cache_clear()


def test_ai_search_enabled_with_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(tmp_path, AI_SEARCH_ENABLED="true", GROQ_API_KEY="sk-test-key"),
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


def test_expenses_disabled_by_default_flag(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(monkeypatch, scenario_env(tmp_path, EXPENSES_ENABLED="false"))
    assert is_expenses_enabled() is False
    assert is_service_enabled("expenses") is False
    get_settings.cache_clear()


def test_expenses_enabled_when_flag_on(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(monkeypatch, scenario_env(tmp_path, EXPENSES_ENABLED="true"))
    assert is_expenses_enabled() is True
    assert is_service_enabled("expenses") is True
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_expenses_api_returns_503_when_disabled(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(monkeypatch, scenario_env(tmp_path, EXPENSES_ENABLED="false"))
    try:
        resp = await client.get("/api/tools/expense-calculator/rates")
        assert resp.status_code == 503
        catalog = await client.get("/api/platform/catalog")
        assert catalog.status_code == 200
        slugs = {item["slug"] for item in catalog.json()["services"]}
        assert "expenses" not in slugs
    finally:
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_sitemap_omits_expense_calculator_when_disabled(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(monkeypatch, scenario_env(tmp_path, EXPENSES_ENABLED="false"))
    try:
        resp = await client.get("/sitemap.xml")
        assert resp.status_code == 200
        assert "/expense-calculator" not in resp.text
    finally:
        get_settings.cache_clear()
