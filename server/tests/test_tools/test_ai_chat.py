from collections.abc import AsyncIterator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from httpx import AsyncClient

from app.core.deps import get_ai_search_service
from app.core.exceptions import ApiError
from app.main import app
from app.services.ai_chat import (
    GEMINI_API_BASE_URL,
    GEMINI_MAX_RETRIES,
    GeminiChatService,
    _gemini_rate_limit_message,
    detect_llm_provider,
)
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
            GEMINI_API_KEY="",
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
    assert resp.status_code == 503
    assert "not configured" in resp.json()["detail"].lower()


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
    assert '"model": "gemini-3.5-flash"' in body


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
    assert body["model"] == "gemini-3.5-flash"
    assert body["provider"] == "gemini"
    assert body["base_url"] == GEMINI_API_BASE_URL
    assert "api_key" not in body
    assert "test-key" not in resp.text


@pytest.mark.asyncio
async def test_ai_chat_config_not_configured_without_key(
    auth_client: AsyncClient,
    missing_api_key: None,
) -> None:
    resp = await auth_client.get(CONFIG_URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["configured"] is False
    assert body["enabled"] is False


@pytest.mark.asyncio
async def test_ai_chat_config_returns_custom_gemini_base_url(
    auth_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(
            tmp_path,
            GEMINI_API_BASE_URL="https://example.test/v1beta",
            GEMINI_CHAT_MODEL="gemini-test",
        ),
    )

    resp = await auth_client.get(CONFIG_URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "gemini"
    assert body["base_url"] == "https://example.test/v1beta"
    assert body["model"] == "gemini-test"


def test_detect_llm_provider_labels() -> None:
    assert detect_llm_provider("") == "gemini"
    assert detect_llm_provider("https://example.com/v1") == "gemini"


def test_gemini_service_normalizes_base_url() -> None:
    service = GeminiChatService(
        api_key="test-key",
        model="gemini-test",
        base_url="https://example.test/v1beta/",
    )

    assert service.provider == "gemini"
    assert service.model == "gemini-test"
    assert service.base_url == "https://example.test/v1beta"


@pytest.mark.asyncio
async def test_gemini_service_reads_text_from_step_start() -> None:
    """Capture initial model_output text delivered on step.start."""
    lines = [
        'data: {"event_type":"interaction.created"}',
        (
            'data: {"event_type":"step.start","index":1,'
            '"step":{"type":"model_output","content":[{"type":"text","text":"Hello"}]}}'
        ),
        'data: {"event_type":"step.delta","index":1,"delta":{"type":"text","text":" world"}}',
    ]
    service = GeminiChatService(api_key="test-key", model="gemini-3.5-flash")

    with patch("app.services.ai_chat.httpx.AsyncClient", _fake_client(lines)):
        chunks = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]

    assert chunks == ["Hello", " world"]


@pytest.mark.asyncio
async def test_gemini_service_skips_contentless_stream_chunks() -> None:
    """Ignore provider bookkeeping chunks and keep yielding text chunks."""
    lines = [
        'data: {"event_type":"interaction.created"}',
        'data: {"event_type":"step.delta","delta":{"type":"thought_signature"}}',
        'data: {"event_type":"step.delta","delta":{"type":"text","text":"Hi"}}',
    ]
    service = GeminiChatService(api_key="test-key", model="gemini-3.5-flash")

    with patch("app.services.ai_chat.httpx.AsyncClient", _fake_client(lines)):
        chunks = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]

    assert chunks == ["Hi"]


@pytest.mark.asyncio
async def test_gemini_service_rejects_stream_without_text() -> None:
    """Return a useful error instead of silently completing an empty stream."""
    lines = [
        'data: {"event_type":"interaction.created"}',
        'data: {"event_type":"step.delta","delta":{"type":"thought_signature"}}',
    ]
    service = GeminiChatService(api_key="test-key", model="gemini-3.5-flash")

    with (
        pytest.raises(ApiError, match="no response text"),
        patch("app.services.ai_chat.httpx.AsyncClient", _fake_client(lines)),
    ):
        _ = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]


def test_gemini_rate_limit_message_includes_retry_after() -> None:
    request = httpx.Request("POST", "https://example.test/v1beta/interactions")
    response = httpx.Response(429, request=request, headers={"Retry-After": "60"})
    assert _gemini_rate_limit_message(response) == (
        "Google Gemini quota exceeded — try again in ~60s"
    )


@pytest.mark.asyncio
async def test_gemini_service_retries_on_429_then_succeeds() -> None:
    """Retry transient Gemini 429 before streaming text."""
    lines = ['data: {"event_type":"step.delta","delta":{"type":"text","text":"Hi"}}']
    service = GeminiChatService(api_key="test-key", model="gemini-3.5-flash")

    with (
        patch("app.services.ai_chat.asyncio.sleep", new_callable=AsyncMock),
        patch(
            "app.services.ai_chat.httpx.AsyncClient",
            _rate_limited_client(fail_count=1, lines=lines),
        ),
    ):
        chunks = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]

    assert chunks == ["Hi"]


@pytest.mark.asyncio
async def test_gemini_service_raises_after_retry_exhausted() -> None:
    """Surface quota error after all Gemini retry attempts fail."""
    service = GeminiChatService(api_key="test-key", model="gemini-3.5-flash")
    max_attempts = GEMINI_MAX_RETRIES + 1

    with (
        patch("app.services.ai_chat.asyncio.sleep", new_callable=AsyncMock),
        patch(
            "app.services.ai_chat.httpx.AsyncClient",
            _rate_limited_client(fail_count=max_attempts, lines=[]),
        ),
        pytest.raises(ApiError, match="Google Gemini quota exceeded"),
    ):
        _ = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]


class _RateLimitedFakeGeminiResponse:
    """Stream response that can fail with HTTP 429."""

    def __init__(
        self,
        lines: list[str],
        *,
        status_code: int | None = None,
    ) -> None:
        self._lines = lines
        self._status_code = status_code

    async def __aenter__(self) -> _RateLimitedFakeGeminiResponse:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def raise_for_status(self) -> None:
        if self._status_code != 429:
            return
        request = httpx.Request("POST", "https://example.test/v1beta/interactions")
        response = httpx.Response(
            429,
            request=request,
            headers={"Retry-After": "1"},
        )
        raise httpx.HTTPStatusError("429", request=request, response=response)

    async def aiter_lines(self) -> AsyncIterator[str]:
        for line in self._lines:
            yield line


class _RateLimitedFakeGeminiClient:
    """HTTP client that returns 429 for the first N stream calls."""

    def __init__(
        self,
        *,
        fail_count: int,
        lines: list[str],
        timeout: float,
    ) -> None:
        self._fail_count = fail_count
        self._lines = lines
        self._calls = 0
        self.timeout = timeout

    async def __aenter__(self) -> _RateLimitedFakeGeminiClient:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def stream(self, *_args: object, **_kwargs: object) -> _RateLimitedFakeGeminiResponse:
        self._calls += 1
        if self._calls <= self._fail_count:
            return _RateLimitedFakeGeminiResponse([], status_code=429)
        return _RateLimitedFakeGeminiResponse(self._lines)


def _rate_limited_client(
    *,
    fail_count: int,
    lines: list[str],
) -> type[_RateLimitedFakeGeminiClient]:
    """Build a fake Gemini client that 429s for the first N stream calls."""
    call_state = {"calls": 0}

    class BoundRateLimitedClient(_RateLimitedFakeGeminiClient):
        def __init__(self, *, timeout: float) -> None:
            super().__init__(fail_count=fail_count, lines=lines, timeout=timeout)

        def stream(self, *_args: object, **_kwargs: object) -> _RateLimitedFakeGeminiResponse:
            call_state["calls"] += 1
            if call_state["calls"] <= fail_count:
                return _RateLimitedFakeGeminiResponse([], status_code=429)
            return _RateLimitedFakeGeminiResponse(lines)

    return BoundRateLimitedClient


class _FakeGeminiResponse:
    """Minimal async stream response for Gemini chat tests."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    async def __aenter__(self) -> _FakeGeminiResponse:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def raise_for_status(self) -> None:
        return None

    async def aiter_lines(self) -> AsyncIterator[str]:
        for line in self._lines:
            yield line


class _FakeGeminiClient:
    """Minimal async HTTP client for Gemini chat tests."""

    def __init__(self, lines: list[str], *, timeout: float) -> None:
        self._lines = lines
        self.timeout = timeout

    async def __aenter__(self) -> _FakeGeminiClient:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def stream(self, *_args: object, **_kwargs: object) -> _FakeGeminiResponse:
        return _FakeGeminiResponse(self._lines)


def _fake_client(lines: list[str]) -> type[_FakeGeminiClient]:
    """Build a fake Gemini HTTP client class bound to stream lines."""

    class BoundFakeGeminiClient(_FakeGeminiClient):
        def __init__(self, *, timeout: float) -> None:
            super().__init__(lines, timeout=timeout)

    return BoundFakeGeminiClient


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
    yield {"done": True, "model": "gemini-3.5-flash"}
