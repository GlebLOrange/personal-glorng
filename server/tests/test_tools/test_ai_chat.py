from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.core.deps import get_ai_registry
from app.main import app
from app.services.ai_chat import AIProviderRegistry

CHAT_URL = "/api/tools/ai-chat"
PROVIDERS_URL = "/api/tools/ai-chat/providers"

GROQ_REGISTRY = AIProviderRegistry({"groq": "test-key"})
EMPTY_REGISTRY = AIProviderRegistry({})

CHAT_PAYLOAD = {
    "provider": "groq",
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Hello"}],
}


@pytest.fixture
def groq_registry() -> None:
    app.dependency_overrides[get_ai_registry] = lambda: GROQ_REGISTRY
    yield
    app.dependency_overrides.pop(get_ai_registry, None)


@pytest.fixture
def empty_registry() -> None:
    app.dependency_overrides[get_ai_registry] = lambda: EMPTY_REGISTRY
    yield
    app.dependency_overrides.pop(get_ai_registry, None)


@pytest.mark.asyncio
async def test_ai_chat_unauthenticated(client: AsyncClient) -> None:
    resp = await client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ai_chat_no_api_key(
    auth_client: AsyncClient, empty_registry: None
) -> None:
    resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert resp.status_code == 503
    assert "not configured" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_ai_chat_invalid_model(
    auth_client: AsyncClient, groq_registry: None
) -> None:
    resp = await auth_client.post(
        CHAT_URL,
        json={**CHAT_PAYLOAD, "model": "not-a-real-model"},
    )
    assert resp.status_code == 400
    assert "Unknown model" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_ai_chat_rejects_system_role(
    auth_client: AsyncClient, groq_registry: None
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
    auth_client: AsyncClient, groq_registry: None
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
async def test_ai_chat_rejects_non_groq_provider(
    auth_client: AsyncClient, groq_registry: None
) -> None:
    resp = await auth_client.post(
        CHAT_URL,
        json={**CHAT_PAYLOAD, "provider": "openai"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_providers_returns_groq_only(
    auth_client: AsyncClient, groq_registry: None
) -> None:
    resp = await auth_client.get(PROVIDERS_URL)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "groq"
    assert "llama-3.3-70b-versatile" in data[0]["models"]


@pytest.mark.asyncio
async def test_ai_chat_success(auth_client: AsyncClient, groq_registry: None) -> None:
    mock_result = {
        "reply": "Hi there",
        "model": "llama-3.3-70b-versatile",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        },
    }
    with patch(
        "app.services.ai_chat.OpenAIService.complete",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)

    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "Hi there"
    assert body["model"] == "llama-3.3-70b-versatile"
    assert body["usage"]["total_tokens"] == 15
