"""Tests for LLM JSON helper base URL support."""

import pytest

from app.services import llm_json


@pytest.mark.asyncio
async def test_complete_json_uses_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeCompletions:
        async def create(self, **kwargs: object) -> object:
            return type(
                "Resp",
                (),
                {
                    "choices": [
                        type(
                            "Choice",
                            (),
                            {"message": type("Msg", (), {"content": '{"ok": true}'})()},
                        )(),
                    ],
                },
            )()

    class FakeChat:
        def __init__(self) -> None:
            self.completions = FakeCompletions()

    class FakeClient:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)
            self.chat = FakeChat()

    monkeypatch.setattr(llm_json, "AsyncOpenAI", FakeClient)

    result = await llm_json.complete_json(
        api_key="test-key",
        model="gpt-test",
        system_prompt="sys",
        user_content="hello",
        base_url="https://api.groq.com/openai/v1",
    )
    assert result == {"ok": True}
    assert captured["base_url"] == "https://api.groq.com/openai/v1"
