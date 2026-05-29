"""Tests for AI chat registry, service, and admin endpoints."""

from collections.abc import Generator
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_ai_registry
from app.core.exceptions import ApiError
from app.core.security import create_access_token
from app.main import app
from app.services.ai_chat import (
    PROVIDERS,
    SYSTEM_PROMPT,
    AIProviderRegistry,
    OpenAIService,
)
from tests.factories import create_user

CHAT_PAYLOAD = {
    "messages": [{"role": "user", "content": "Hello"}],
    "provider": "deepseek",
}

MOCK_COMPLETION = {
    "reply": "Hi",
    "model": "deepseek-chat",
    "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
}

PROVIDERS_URL = "/api/tools/ai-chat/providers"
CHAT_URL = "/api/tools/ai-chat"


def registry_with_keys(**keys: str) -> AIProviderRegistry:
    return AIProviderRegistry(api_keys=dict(keys))


@pytest.fixture
def ai_registry() -> Generator[AIProviderRegistry, None, None]:
    registry = registry_with_keys(deepseek="test-key")
    app.dependency_overrides[get_ai_registry] = lambda: registry
    yield registry
    app.dependency_overrides.pop(get_ai_registry, None)


def _api_status_error(exc_cls: type, message: str) -> Exception:
    return exc_cls(message, response=MagicMock(status_code=400), body=None)


def _fake_completion(
    content: str = "Hi",
    model: str = "deepseek-chat",
) -> SimpleNamespace:
    return SimpleNamespace(
        model=model,
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=SimpleNamespace(
            prompt_tokens=1,
            completion_tokens=2,
            total_tokens=3,
        ),
    )


# --- AIProviderRegistry (unit) ---


def test_available_providers_filters_by_key() -> None:
    registry = registry_with_keys(deepseek="sk-test", openai="sk-unused")
    providers = registry.available_providers()

    assert len(providers) == 1
    assert providers[0]["id"] == "deepseek"
    assert providers[0]["models"] == PROVIDERS["deepseek"].models
    assert providers[0]["default_model"] == PROVIDERS["deepseek"].default_model


def test_build_service_unknown_provider() -> None:
    registry = registry_with_keys(deepseek="sk-test")

    with pytest.raises(ApiError) as exc_info:
        registry.build_service("unknown")

    assert exc_info.value.status_code == 400
    assert "Unknown provider" in exc_info.value.message


def test_build_service_missing_key() -> None:
    registry = registry_with_keys()

    with pytest.raises(ApiError) as exc_info:
        registry.build_service("deepseek")

    assert exc_info.value.status_code == 503
    assert "deepseek" in exc_info.value.message


def test_build_service_default_model() -> None:
    registry = registry_with_keys(deepseek="sk-test")
    service = registry.build_service("deepseek")

    assert service._model == PROVIDERS["deepseek"].default_model


def test_build_service_explicit_model() -> None:
    registry = registry_with_keys(deepseek="sk-test")
    service = registry.build_service("deepseek", model="deepseek-reasoner")

    assert service._model == "deepseek-reasoner"


# --- OpenAIService.complete (unit) ---


@pytest.mark.asyncio
async def test_complete_success_prepends_system_prompt() -> None:
    mock_create = AsyncMock(return_value=_fake_completion())
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    with patch("app.services.ai_chat.AsyncOpenAI", return_value=mock_client):
        service = OpenAIService(api_key="sk-test", model="deepseek-chat")
        result = await service.complete([{"role": "user", "content": "Hello"}])

    assert result == MOCK_COMPLETION
    mock_create.assert_awaited_once()
    messages = mock_create.await_args.kwargs["messages"]
    assert messages[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert messages[1] == {"role": "user", "content": "Hello"}


@pytest.mark.asyncio
async def test_complete_authentication_error() -> None:
    mock_create = AsyncMock(
        side_effect=_api_status_error(AuthenticationError, "bad key")
    )
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    with patch("app.services.ai_chat.AsyncOpenAI", return_value=mock_client):
        service = OpenAIService(api_key="sk-test", model="deepseek-chat")
        with pytest.raises(ApiError) as exc_info:
            await service.complete([{"role": "user", "content": "Hi"}])

    assert exc_info.value.status_code == 502
    assert "API key" in exc_info.value.message


@pytest.mark.asyncio
async def test_complete_rate_limit_error() -> None:
    mock_create = AsyncMock(
        side_effect=_api_status_error(RateLimitError, "rate limited")
    )
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    with patch("app.services.ai_chat.AsyncOpenAI", return_value=mock_client):
        service = OpenAIService(api_key="sk-test", model="deepseek-chat")
        with pytest.raises(ApiError) as exc_info:
            await service.complete([{"role": "user", "content": "Hi"}])

    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_complete_timeout_error() -> None:
    mock_create = AsyncMock(side_effect=APITimeoutError(request=MagicMock()))
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    with patch("app.services.ai_chat.AsyncOpenAI", return_value=mock_client):
        service = OpenAIService(api_key="sk-test", model="deepseek-chat")
        with pytest.raises(ApiError) as exc_info:
            await service.complete([{"role": "user", "content": "Hi"}])

    assert exc_info.value.status_code == 504


@pytest.mark.asyncio
async def test_complete_connection_error() -> None:
    mock_create = AsyncMock(side_effect=APIConnectionError(request=MagicMock()))
    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    with patch("app.services.ai_chat.AsyncOpenAI", return_value=mock_client):
        service = OpenAIService(api_key="sk-test", model="deepseek-chat")
        with pytest.raises(ApiError) as exc_info:
            await service.complete([{"role": "user", "content": "Hi"}])

    assert exc_info.value.status_code == 502
    assert "unreachable" in exc_info.value.message


# --- GET /providers (integration) ---


@pytest.mark.asyncio
async def test_providers_unauthorized(client: AsyncClient) -> None:
    resp = await client.get(PROVIDERS_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_providers_forbidden_non_admin(
    client: AsyncClient, db: AsyncSession
) -> None:
    user = await create_user(db, email="user@glorng.dev", is_admin=False)
    client.headers["Authorization"] = f"Bearer {create_access_token(str(user.id))}"

    resp = await client.get(PROVIDERS_URL)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_providers_lists_configured(
    auth_client: AsyncClient, ai_registry: AIProviderRegistry
) -> None:
    resp = await auth_client.get(PROVIDERS_URL)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "deepseek"
    assert data[0]["default_model"] == PROVIDERS["deepseek"].default_model


@pytest.mark.asyncio
async def test_providers_empty_when_no_keys(auth_client: AsyncClient) -> None:
    app.dependency_overrides[get_ai_registry] = lambda: registry_with_keys()
    try:
        resp = await auth_client.get(PROVIDERS_URL)
        assert resp.status_code == 200
        assert resp.json() == []
    finally:
        app.dependency_overrides.pop(get_ai_registry, None)


# --- POST /chat (integration) ---


@pytest.mark.asyncio
async def test_chat_unauthorized(client: AsyncClient) -> None:
    resp = await client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_chat_forbidden_non_admin(
    client: AsyncClient, db: AsyncSession
) -> None:
    user = await create_user(db, email="chat-user@glorng.dev", is_admin=False)
    client.headers["Authorization"] = f"Bearer {create_access_token(str(user.id))}"

    resp = await client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_chat_success(
    auth_client: AsyncClient, ai_registry: AIProviderRegistry
) -> None:
    with patch(
        "app.services.ai_chat.OpenAIService.complete",
        new_callable=AsyncMock,
        return_value=MOCK_COMPLETION,
    ):
        resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)

    assert resp.status_code == 200
    assert resp.json() == MOCK_COMPLETION


@pytest.mark.asyncio
async def test_chat_invalid_role(auth_client: AsyncClient, ai_registry: AIProviderRegistry) -> None:
    payload = {
        "messages": [{"role": "invalid", "content": "Hello"}],
        "provider": "deepseek",
    }
    resp = await auth_client.post(CHAT_URL, json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_chat_unknown_provider(
    auth_client: AsyncClient, ai_registry: AIProviderRegistry
) -> None:
    payload = {**CHAT_PAYLOAD, "provider": "unknown"}
    resp = await auth_client.post(CHAT_URL, json=payload)

    assert resp.status_code == 400
    assert "provider" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_chat_provider_without_key(auth_client: AsyncClient) -> None:
    app.dependency_overrides[get_ai_registry] = lambda: registry_with_keys()
    try:
        resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)

        assert resp.status_code == 503
        assert "deepseek" in resp.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(get_ai_registry, None)


@pytest.mark.asyncio
async def test_chat_custom_model_forwarded(
    auth_client: AsyncClient, ai_registry: AIProviderRegistry
) -> None:
    with patch(
        "app.services.ai_chat.OpenAIService.complete",
        new_callable=AsyncMock,
        return_value=MOCK_COMPLETION,
    ) as mock_complete:
        payload = {**CHAT_PAYLOAD, "model": "deepseek-reasoner"}
        resp = await auth_client.post(CHAT_URL, json=payload)

    assert resp.status_code == 200
    service = ai_registry.build_service("deepseek", model="deepseek-reasoner")
    assert service._model == "deepseek-reasoner"
    mock_complete.assert_awaited_once()
