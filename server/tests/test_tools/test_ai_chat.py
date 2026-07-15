from collections.abc import AsyncIterator
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from httpx import AsyncClient

from app.core.deps import get_groq_chat_service
from app.core.exceptions import ApiError
from app.core.security import create_access_token
from app.main import app
from app.services.ai_chat import (
    GROQ_API_BASE_URL,
    GROQ_MAX_RETRIES,
    GroqChatService,
    _rate_limit_message,
    _retry_after_seconds,
    _should_retry_rate_limit_429,
    detect_llm_provider,
)
from app.settings import get_settings
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file, scenario_env
from tests.factories import create_user

CHAT_URL = "/api/tools/ai-chat"
CONFIG_URL = "/api/tools/ai-chat/config"

CHAT_PAYLOAD = {
    "messages": [{"role": "user", "content": "Hello"}],
}


@pytest.fixture(autouse=True)
def enable_ai_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "ai-chat.env")


@pytest.fixture
def groq_chat_service() -> None:
    def _service() -> GroqChatService:
        return GroqChatService(
            api_key="test-key",
            model="llama-3.3-70b-versatile",
        )

    app.dependency_overrides[get_groq_chat_service] = _service
    yield
    app.dependency_overrides.pop(get_groq_chat_service, None)


@pytest.fixture
def missing_api_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(
            tmp_path,
            base=ENV_SCENARIOS_DIR / "ai-chat.env",
            GROQ_API_KEY="",
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
    groq_chat_service: None,
) -> None:
    resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert resp.status_code == 503
    assert "not configured" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_ai_chat_rejects_system_role(
    auth_client: AsyncClient,
    groq_chat_service: None,
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
    groq_chat_service: None,
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
    groq_chat_service: None,
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
    groq_chat_service: None,
) -> None:
    with patch.object(
        GroqChatService,
        "stream",
        side_effect=_mock_stream,
    ):
        resp = await auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")

    body = resp.text
    assert '"sources"' not in body
    assert 'data: {"delta": "Hi "}' in body
    assert 'data: {"delta": "there"}' in body
    assert '"done": true' in body
    assert '"model": "llama-3.3-70b-versatile"' in body


@pytest.fixture
async def limited_auth_client(
    client: AsyncClient,
    registry,
) -> AsyncClient:
    user = await create_user(
        registry,
        email="reader@example.com",
        permissions=["ai-chat:read", "ai-chat:write"],
    )
    token = create_access_token(str(user.public_id))
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.mark.asyncio
async def test_ai_chat_requires_superuser(
    limited_auth_client: AsyncClient,
    groq_chat_service: None,
) -> None:
    chat_resp = await limited_auth_client.post(CHAT_URL, json=CHAT_PAYLOAD)
    assert chat_resp.status_code == 403

    config_resp = await limited_auth_client.get(CONFIG_URL)
    assert config_resp.status_code == 403


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
    assert body["model"] == "llama-3.3-70b-versatile"
    assert body["provider"] == "groq"
    assert body["base_url"] == GROQ_API_BASE_URL
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
async def test_ai_chat_config_returns_custom_groq_base_url(
    auth_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    activate_env_file(
        monkeypatch,
        scenario_env(
            tmp_path,
            GROQ_API_BASE_URL="https://example.test/v1",
            GROQ_CHAT_MODEL="llama-test",
        ),
    )

    resp = await auth_client.get(CONFIG_URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "groq"
    assert body["base_url"] == "https://example.test/v1"
    assert body["model"] == "llama-test"


def test_detect_llm_provider_labels() -> None:
    assert detect_llm_provider("") == "groq"
    assert detect_llm_provider("https://example.com/v1") == "groq"


def test_groq_service_normalizes_base_url() -> None:
    service = GroqChatService(
        api_key="test-key",
        model="llama-test",
        base_url="https://example.test/v1/",
    )

    assert service.provider == "groq"
    assert service.model == "llama-test"
    assert service.base_url == "https://example.test/v1"


@pytest.mark.asyncio
async def test_groq_service_streams_text_deltas() -> None:
    """Yield assistant text from OpenAI-compatible SSE chunks."""
    lines = [
        'data: {"choices":[{"delta":{"content":"Hello"}}]}',
        'data: {"choices":[{"delta":{"content":" world"}}]}',
        "data: [DONE]",
    ]
    service = GroqChatService(api_key="test-key", model="llama-3.3-70b-versatile")

    with patch("app.services.ai_chat.httpx.AsyncClient", _fake_client(lines)):
        chunks = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]

    assert chunks == ["Hello", " world"]


@pytest.mark.asyncio
async def test_groq_service_skips_contentless_stream_chunks() -> None:
    """Ignore empty deltas and keep yielding text chunks."""
    lines = [
        'data: {"choices":[{"delta":{}}]}',
        'data: {"choices":[{"delta":{"content":"Hi"}}]}',
    ]
    service = GroqChatService(api_key="test-key", model="llama-3.3-70b-versatile")

    with patch("app.services.ai_chat.httpx.AsyncClient", _fake_client(lines)):
        chunks = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]

    assert chunks == ["Hi"]


@pytest.mark.asyncio
async def test_groq_service_rejects_stream_without_text() -> None:
    """Return a useful error instead of silently completing an empty stream."""
    lines = [
        'data: {"choices":[{"delta":{}}]}',
        "data: [DONE]",
    ]
    service = GroqChatService(api_key="test-key", model="llama-3.3-70b-versatile")

    with (
        pytest.raises(ApiError, match="no response text"),
        patch("app.services.ai_chat.httpx.AsyncClient", _fake_client(lines)),
    ):
        _ = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]


def test_rate_limit_message_includes_retry_after() -> None:
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    response = httpx.Response(429, request=request, headers={"Retry-After": "60"})
    assert _rate_limit_message(response) == (
        "Groq rate limit exceeded — try again in ~60s"
    )


def test_should_retry_rate_limit_429_only_for_short_retry_after() -> None:
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    short_wait = httpx.Response(429, request=request, headers={"Retry-After": "30"})
    long_wait = httpx.Response(429, request=request, headers={"Retry-After": "31"})
    no_hint = httpx.Response(429, request=request)

    assert _should_retry_rate_limit_429(short_wait) is True
    assert _should_retry_rate_limit_429(long_wait) is False
    assert _should_retry_rate_limit_429(no_hint) is False


def test_retry_after_seconds_reads_header() -> None:
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    response = httpx.Response(429, request=request, headers={"Retry-After": "45"})
    assert _retry_after_seconds(response) == 45


@pytest.mark.asyncio
async def test_groq_service_retries_on_429_then_succeeds() -> None:
    """Retry short-lived Groq 429 when Retry-After is present."""
    lines = ['data: {"choices":[{"delta":{"content":"Hi"}}]}']
    service = GroqChatService(api_key="test-key", model="llama-3.3-70b-versatile")

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
async def test_groq_service_raises_after_retry_exhausted() -> None:
    """Surface quota error after short-lived 429 retries are exhausted."""
    service = GroqChatService(api_key="test-key", model="llama-3.3-70b-versatile")
    max_attempts = GROQ_MAX_RETRIES + 1

    with (
        patch("app.services.ai_chat.asyncio.sleep", new_callable=AsyncMock),
        patch(
            "app.services.ai_chat.httpx.AsyncClient",
            _rate_limited_client(fail_count=max_attempts, lines=[]),
        ),
        pytest.raises(ApiError, match="Groq rate limit exceeded"),
    ):
        _ = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]


@pytest.mark.asyncio
async def test_groq_service_fails_fast_on_429_without_retry_after() -> None:
    """Do not burn extra quota when Groq omits a short retry hint."""
    service = GroqChatService(api_key="test-key", model="llama-3.3-70b-versatile")
    client_cls, call_state = _quota_error_client(retry_after=None)

    with (
        patch("app.services.ai_chat.httpx.AsyncClient", client_cls),
        pytest.raises(ApiError, match="Groq rate limit exceeded"),
    ):
        _ = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]

    assert call_state["calls"] == 1


@pytest.mark.asyncio
async def test_groq_service_fails_fast_on_429_long_retry_after() -> None:
    """Do not wait out long quota windows inside one request."""
    service = GroqChatService(api_key="test-key", model="llama-3.3-70b-versatile")
    client_cls, call_state = _quota_error_client(retry_after="120")

    with (
        patch("app.services.ai_chat.httpx.AsyncClient", client_cls),
        pytest.raises(ApiError, match="Groq rate limit exceeded"),
    ):
        _ = [chunk async for chunk in service.stream(CHAT_PAYLOAD["messages"])]

    assert call_state["calls"] == 1


class _RateLimitedFakeGroqResponse:
    """Stream response that can fail with HTTP 429."""

    def __init__(
        self,
        lines: list[str],
        *,
        status_code: int | None = None,
        retry_after: str | None = "1",
    ) -> None:
        self._lines = lines
        self._status_code = status_code
        self._retry_after = retry_after

    async def __aenter__(self) -> _RateLimitedFakeGroqResponse:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def raise_for_status(self) -> None:
        if self._status_code != 429:
            return
        request = httpx.Request("POST", "https://example.test/v1/chat/completions")
        headers = {"Retry-After": self._retry_after} if self._retry_after else {}
        response = httpx.Response(
            429,
            request=request,
            headers=headers,
        )
        raise httpx.HTTPStatusError("429", request=request, response=response)

    async def aiter_lines(self) -> AsyncIterator[str]:
        for line in self._lines:
            yield line


class _RateLimitedFakeGroqClient:
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

    async def __aenter__(self) -> _RateLimitedFakeGroqClient:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def stream(self, *_args: object, **_kwargs: object) -> _RateLimitedFakeGroqResponse:
        self._calls += 1
        if self._calls <= self._fail_count:
            return _RateLimitedFakeGroqResponse([], status_code=429)
        return _RateLimitedFakeGroqResponse(self._lines)


def _rate_limited_client(
    *,
    fail_count: int,
    lines: list[str],
) -> type[_RateLimitedFakeGroqClient]:
    """Build a fake Groq client that 429s for the first N stream calls."""
    call_state = {"calls": 0}

    class BoundRateLimitedClient(_RateLimitedFakeGroqClient):
        def __init__(self, *, timeout: float) -> None:
            super().__init__(fail_count=fail_count, lines=lines, timeout=timeout)

        def stream(self, *_args: object, **_kwargs: object) -> _RateLimitedFakeGroqResponse:
            call_state["calls"] += 1
            if call_state["calls"] <= fail_count:
                return _RateLimitedFakeGroqResponse([], status_code=429)
            return _RateLimitedFakeGroqResponse(lines)

    return BoundRateLimitedClient


def _quota_error_client(
    *,
    retry_after: str | None,
) -> tuple[type, dict[str, int]]:
    """Build a fake Groq client that always returns one quota error."""
    call_state = {"calls": 0}

    class BoundQuotaErrorClient:
        def __init__(self, *, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self) -> BoundQuotaErrorClient:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        def stream(
            self,
            *_args: object,
            **_kwargs: object,
        ) -> _RateLimitedFakeGroqResponse:
            call_state["calls"] += 1
            return _RateLimitedFakeGroqResponse(
                [],
                status_code=429,
                retry_after=retry_after,
            )

    return BoundQuotaErrorClient, call_state


class _FakeGroqResponse:
    """Minimal async stream response for Groq chat tests."""

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    async def __aenter__(self) -> _FakeGroqResponse:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def raise_for_status(self) -> None:
        return None

    async def aiter_lines(self) -> AsyncIterator[str]:
        for line in self._lines:
            yield line


class _FakeGroqClient:
    """Minimal async HTTP client for Groq chat tests."""

    def __init__(self, lines: list[str], *, timeout: float) -> None:
        self._lines = lines
        self.timeout = timeout

    async def __aenter__(self) -> _FakeGroqClient:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def stream(self, *_args: object, **_kwargs: object) -> _FakeGroqResponse:
        return _FakeGroqResponse(self._lines)


def _fake_client(lines: list[str]) -> type[_FakeGroqClient]:
    """Build a fake Groq HTTP client class bound to stream lines."""

    class BoundFakeGroqClient(_FakeGroqClient):
        def __init__(self, *, timeout: float) -> None:
            super().__init__(lines, timeout=timeout)

    return BoundFakeGroqClient


async def _mock_stream(*_args: object, **_kwargs: object) -> AsyncIterator[str]:
    """Yield sample chat text chunks."""
    for part in ("Hi ", "there"):
        yield part
