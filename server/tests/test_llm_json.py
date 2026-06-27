"""Tests for Gemini JSON helper base URL support."""

import pytest

from app.services import llm_json


@pytest.mark.asyncio
async def test_complete_json_uses_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"output_text": '{"ok": true}'}

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
        model="gemini-test",
        system_prompt="sys",
        user_content="hello",
        api_base_url="https://example.test/v1beta",
    )
    assert result == {"ok": True}
    assert captured["url"] == "https://example.test/v1beta/interactions"
    assert captured["headers"] == {
        "Content-Type": "application/json",
        "x-goog-api-key": "test-key",
    }
