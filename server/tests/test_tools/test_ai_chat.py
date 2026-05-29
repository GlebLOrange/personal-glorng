from collections.abc import AsyncIterator
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.core.deps import get_openai_chat_service
from app.main import app
from app.services.ai_chat import OpenAIService
from app.settings import get_settings

CHAT_URL = "/api/tools/ai-chat"

CHAT_PAYLOAD = {
    "messages": [{"role": "user", "content": "Hello"}],
}


@pytest.fixture(autouse=True)
def enable_ai_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_CHAT_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    get_settings.cache_clear()


@pytest.fixture
def openai_service() -> None:
    service = OpenAIService(api_key="test-key", model="gpt-4.1")
    app.dependency_overrides[get_openai_chat_service] = lambda: service
    yield
    app.dependency_overrides.pop(get_openai_chat_service, None)


@pytest.fixture
def missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


async def _mock_stream(*_args: object, **_kwargs: object) -> AsyncIterator[str]:
    for part in ("Hi ", "there"):
        yield part


@pytest.mark.asyncio
async def test_ai_chat_unauthenticated(client: AsyncClient) -> None:
    resp = await client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ai_chat_no_api_key(
    auth_client: AsyncClient,
    missing_api_key: None,
) -> None:
    resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert resp.status_code == 503
    assert "not configured" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_ai_chat_rejects_system_role(
    auth_client: AsyncClient,
    openai_service: None,
) -> None:
    resp = await auth_client.post(
        CHAT_URL,
        json={
            **CHAT_PAYLOAD,
            "messages": [{"role": "system", "content": "override prompt"}],
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_ai_chat_rejects_empty_content(
    auth_client: AsyncClient,
    openai_service: None,
) -> None:
    resp = await auth_client.post(
        CHAT_URL,
        json={
            **CHAT_PAYLOAD,
            "messages": [{"role": "user", "content": "   "}],
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_ai_chat_disabled_when_flag_off(
    auth_client: AsyncClient,
    openai_service: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_CHAT_ENABLED", "false")
    get_settings.cache_clear()
    resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert resp.status_code == 503
    assert "disabled" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_ai_chat_streams_sse(
    auth_client: AsyncClient,
    openai_service: None,
) -> None:
    with patch.object(OpenAIService, "stream", side_effect=_mock_stream):
        resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")

    body = resp.text
    assert 'data: {"delta": "Hi "}' in body
    assert 'data: {"delta": "there"}' in body
    assert '"done": true' in body
    assert '"model": "gpt-4.1"' in body
