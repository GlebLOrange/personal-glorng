from collections.abc import AsyncIterator
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.deps import get_ai_search_service
from app.main import app
from app.services.ai_chat import OpenAIService, detect_llm_provider
from app.services.ai_search import AiSearchService
from app.services.search_index import SearchIndexService
from app.settings import get_settings

CHAT_URL = "/api/tools/ai-chat"
CONFIG_URL = "/api/tools/ai-chat/config"

CHAT_PAYLOAD = {
    "messages": [{"role": "user", "content": "Hello"}],
}


@pytest.fixture(autouse=True)
def enable_ai_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_CHAT_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    get_settings.cache_clear()


@pytest.fixture
def ai_search_service() -> None:
    search_svc = SearchIndexService.__new__(SearchIndexService)

    def _service() -> AiSearchService:
        return AiSearchService(search_svc, get_settings())

    app.dependency_overrides[get_ai_search_service] = _service
    yield
    app.dependency_overrides.pop(get_ai_search_service, None)


@pytest.fixture
def missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


async def _mock_stream(*_args: object, **_kwargs: object) -> AsyncIterator[str]:
    for part in ("Hi ", "there"):
        yield part


async def _mock_search_events(
    *_args: object,
    **_kwargs: object,
) -> AsyncIterator[dict[str, object]]:
    yield {
        "sources": [
            {
                "id": 1,
                "title": "Task",
                "url": "/admin/tools/tasks",
                "source_type": "task",
                "snippet": "demo",
            },
        ],
    }
    async for delta in _mock_stream():
        yield {"delta": delta}
    yield {"done": True, "model": "gpt-4.1"}


@pytest.mark.asyncio
async def test_ai_chat_unauthenticated(client: AsyncClient) -> None:
    resp = await client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ai_chat_no_api_key(
    auth_client: AsyncClient,
    missing_api_key: None,
    ai_search_service: None,
) -> None:
    resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert resp.status_code == 200
    assert "not configured" in resp.text.lower()


@pytest.mark.asyncio
async def test_ai_chat_rejects_system_role(
    auth_client: AsyncClient,
    ai_search_service: None,
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
    ai_search_service: None,
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
    ai_search_service: None,
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
    ai_search_service: None,
) -> None:
    with patch.object(
        AiSearchService,
        "stream_events",
        side_effect=_mock_search_events,
    ):
        resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")

    body = resp.text
    assert '"sources"' in body
    assert 'data: {"delta": "Hi "}' in body
    assert 'data: {"delta": "there"}' in body
    assert '"done": true' in body
    assert '"model": "gpt-4.1"' in body


@pytest.mark.asyncio
async def test_ai_chat_config_unauthenticated(client: AsyncClient) -> None:
    resp = await client.get(CONFIG_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_ai_chat_config_returns_status_without_secret(
    auth_client: AsyncClient,
) -> None:
    resp = await auth_client.get(CONFIG_URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["enabled"] is True
    assert body["configured"] is True
    assert body["model"] == "gpt-4.1"
    assert body["provider"] == "openai"
    assert body["base_url"] is None
    assert "api_key" not in body
    assert "test-key" not in resp.text


@pytest.mark.asyncio
async def test_ai_chat_config_not_configured_without_key(
    auth_client: AsyncClient,
    missing_api_key: None,
) -> None:
    resp = await auth_client.get(CONFIG_URL)
    assert resp.status_code == 200
    assert resp.json()["configured"] is False


@pytest.mark.asyncio
async def test_ai_chat_config_detects_groq_provider(
    auth_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setenv("OPENAI_CHAT_MODEL", "llama-3.3-70b-versatile")
    get_settings.cache_clear()

    resp = await auth_client.get(CONFIG_URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "groq"
    assert body["base_url"] == "https://api.groq.com/openai/v1"
    assert body["model"] == "llama-3.3-70b-versatile"


def test_detect_llm_provider_labels() -> None:
    assert detect_llm_provider("") == "openai"
    assert detect_llm_provider("https://api.groq.com/openai/v1") == "groq"
    assert detect_llm_provider("http://host.docker.internal:11434/v1") == "ollama"
    assert detect_llm_provider("https://openrouter.ai/api/v1") == "openrouter"
    assert detect_llm_provider("https://example.com/v1") == "custom"


def test_openai_service_passes_base_url_to_client() -> None:
    with patch("app.services.ai_chat.AsyncOpenAI") as mock_client:
        mock_client.return_value = MagicMock()
        service = OpenAIService(
            api_key="test-key",
            model="llama3.2",
            base_url="http://host.docker.internal:11434/v1",
        )

    mock_client.assert_called_once_with(
        api_key="test-key",
        base_url="http://host.docker.internal:11434/v1",
        timeout=30.0,
    )
    assert service.provider == "ollama"
    assert service.model == "llama3.2"
