from collections.abc import AsyncIterator
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.deps import get_ai_search_service
from app.core.exceptions import ApiError
from app.main import app
from app.services.ai_chat import OpenAIService, detect_llm_provider
from app.services.ai_search import AiSearchService
from app.services.search_index import SearchIndexService
from app.settings import get_settings
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file, scenario_env

CHAT_URL = "/api/tools/ai-chat"
CONFIG_URL = "/api/tools/ai-chat/config"

CHAT_PAYLOAD = {
    "messages": [{"role": "user", "content": "Hello"}],
}


@pytest.fixture(autouse=True)
def enable_ai_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "ai-chat.env")


@pytest.fixture
def ai_search_service() -> None:
    search_svc = MagicMock(spec=SearchIndexService)
    search_svc.search = AsyncMock(return_value=[])

    def _service() -> AiSearchService:
        return AiSearchService(search_svc, get_settings())

    app.dependency_overrides[get_ai_search_service] = _service
    yield
    app.dependency_overrides.pop(get_ai_search_service, None)


@pytest.fixture
def missing_api_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(
            tmp_path,
            base=ENV_SCENARIOS_DIR / "ai-chat.env",
            OPENAI_API_KEY="",
        ),
    )
    yield
    get_settings.cache_clear()


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
    tmp_path: Path,
) -> None:
    activate_env_file(monkeypatch, scenario_env(tmp_path, AI_CHAT_ENABLED="false"))
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
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(
            tmp_path,
            LLM_BASE_URL="https://api.groq.com/openai/v1",
            OPENAI_CHAT_MODEL="llama-3.3-70b-versatile",
        ),
    )

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


@pytest.mark.asyncio
async def test_openai_service_skips_contentless_stream_chunks() -> None:
    """Ignore provider bookkeeping chunks and keep yielding text chunks."""
    service = _openai_service_with_chunks(
        [
            SimpleNamespace(choices=[]),
            _provider_chunk(None),
            _provider_chunk("Hi"),
        ]
    )

    chunks = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]

    assert chunks == ["Hi"]


@pytest.mark.asyncio
async def test_openai_service_rejects_stream_without_text() -> None:
    """Return a useful error instead of silently completing an empty stream."""
    service = _openai_service_with_chunks(
        [
            SimpleNamespace(choices=[]),
            _provider_chunk(None),
        ]
    )

    with pytest.raises(ApiError, match="no response text"):
        _ = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]


def _provider_chunk(content: str | None) -> SimpleNamespace:
    """Build the minimal OpenAI-compatible stream chunk shape used by tests."""
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                delta=SimpleNamespace(content=content),
            )
        ]
    )


def _openai_service_with_chunks(chunks: list[object]) -> OpenAIService:
    """Build a chat service with a mocked streaming provider response."""
    with patch("app.services.ai_chat.AsyncOpenAI") as mock_client:
        client = MagicMock()
        client.chat.completions.create = AsyncMock(return_value=_mock_provider_chunks(chunks))
        mock_client.return_value = client
        return OpenAIService(api_key="test-key", model="gpt-4.1")


async def _mock_provider_chunks(chunks: list[object]) -> AsyncIterator[object]:
    """Yield mock provider chunks in streaming order."""
    for chunk in chunks:
        yield chunk


async def _mock_stream(*_args: object, **_kwargs: object) -> AsyncIterator[str]:
    """Yield sample chat text chunks."""
    for part in ("Hi ", "there"):
        yield part


async def _mock_search_events(
    *_args: object,
    **_kwargs: object,
) -> AsyncIterator[dict[str, object]]:
    """Yield sample retrieve-then-generate SSE events."""
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
