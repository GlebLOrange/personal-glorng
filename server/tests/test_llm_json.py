"""Tests for Groq JSON helper base URL support."""

import httpx
import pytest

from app.core.exceptions import ApiError
from app.services import llm_json


@pytest.mark.asyncio
async def test_complete_json_uses_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "choices": [
                    {"message": {"content": '{"ok": true}'}},
                ],
            }

    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            captured["timeout"] = timeout

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def post(self, url: str, **kwargs: object) -> FakeResponse:
            captured["url"] = url
            captured.update(kwargs)
            return FakeResponse()

    monkeypatch.setattr(llm_json.httpx, "AsyncClient", FakeClient)

    result = await llm_json.complete_json(
        api_key="test-key",
        model="llama-test",
        system_prompt="sys",
        user_content="hello",
        api_base_url="https://example.test/v1",
    )
    assert result == {"ok": True}
    assert captured["url"] == "https://example.test/v1/chat/completions"
    assert captured["headers"] == {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-key",
    }


@pytest.mark.asyncio
async def test_complete_json_fails_fast_on_429_without_retry_after(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not retry JSON calls when Groq omits a short retry hint."""
    call_state = {"calls": 0}

    class FakeResponse:
        def raise_for_status(self) -> None:
            request = httpx.Request("POST", "https://example.test/v1/chat/completions")
            response = httpx.Response(429, request=request)
            raise httpx.HTTPStatusError("429", request=request, response=response)

    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *_args: object) -> None:
            return None

        async def post(self, *_args: object, **_kwargs: object) -> FakeResponse:
            call_state["calls"] += 1
            return FakeResponse()

    monkeypatch.setattr(llm_json.httpx, "AsyncClient", FakeClient)

    with pytest.raises(ApiError, match="Groq rate limit exceeded"):
        await llm_json.complete_json(
            api_key="test-key",
            model="llama-test",
            system_prompt="sys",
            user_content="hello",
            api_base_url="https://example.test/v1",
        )

    assert call_state["calls"] == 1
