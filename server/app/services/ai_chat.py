import json
from collections.abc import AsyncIterator

import httpx

from app.core.exceptions import ApiError
from app.core.logging import logger

GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
SYSTEM_PROMPT = (
    "You are a concise, helpful assistant embedded in a developer"
    " portfolio admin panel. Keep responses short and technical"
    " unless asked otherwise."
)


def _normalized_base_url(base_url: str) -> str:
    """Return a Gemini API base URL without trailing slashes."""
    return (base_url.strip() or GEMINI_API_BASE_URL).rstrip("/")


def detect_llm_provider(_base_url: str = "") -> str:
    """Return the configured LLM provider label."""
    return "gemini"


def _headers(api_key: str) -> dict[str, str]:
    """Return Gemini REST headers."""
    return {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }


def _stream_headers(api_key: str) -> dict[str, str]:
    """Return Gemini REST headers for SSE streaming."""
    return {
        **_headers(api_key),
        "Accept": "text/event-stream",
    }


def _text_from_content(content: object) -> str | None:
    """Join text blocks from a Gemini step content array."""
    if not isinstance(content, list):
        return None
    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict) or item.get("type") != "text":
            continue
        text = item.get("text")
        if isinstance(text, str) and text:
            parts.append(text)
    return "".join(parts) if parts else None


def _format_chat_input(
    messages: list[dict[str, str]],
    *,
    system_prompt: str,
) -> str:
    """Convert local chat messages into a single Gemini text input."""
    user_messages = [m for m in messages if m.get("role") != "system"]
    turns = "\n".join(
        f"{message.get('role', 'user').title()}: {message.get('content', '')}"
        for message in user_messages
    )
    return f"{system_prompt}\n\nConversation:\n{turns}\n\nAssistant:"


def _stream_text_chunk(line: str) -> str | None:
    """Extract assistant text from one Gemini SSE data line."""
    if not line.startswith("data: "):
        return None
    raw = line.removeprefix("data: ").strip()
    if not raw or raw == "[DONE]":
        return None
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Gemini stream returned invalid JSON chunk")
        return None
    if not isinstance(event, dict):
        return None

    event_type = event.get("event_type")
    if event_type == "step.delta":
        delta = event.get("delta")
        if not isinstance(delta, dict) or delta.get("type") != "text":
            return None
        text = delta.get("text")
        return text if isinstance(text, str) else None

    if event_type == "step.start":
        step = event.get("step")
        if not isinstance(step, dict) or step.get("type") != "model_output":
            return None
        return _text_from_content(step.get("content"))

    return None


def raise_gemini_http_error(exc: httpx.HTTPStatusError) -> None:
    """Map Gemini HTTP errors to local API errors."""
    status_code = exc.response.status_code
    if status_code in {401, 403}:
        raise ApiError(502, "Invalid Gemini API key") from None
    if status_code == 429:
        raise ApiError(429, "Gemini rate limit exceeded — try again shortly") from None
    if status_code >= 500:
        raise ApiError(502, "Gemini API unreachable") from None
    logger.error("Gemini API request failed", context={"status_code": status_code})
    raise ApiError(502, "Gemini API request failed") from None


class GeminiChatService:
    """Async Gemini chat client with streaming text output."""

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        base_url: str = GEMINI_API_BASE_URL,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = _normalized_base_url(base_url)

    @property
    def model(self) -> str:
        """Return the configured Gemini model."""
        return self._model

    @property
    def base_url(self) -> str:
        """Return the configured Gemini API base URL."""
        return self._base_url

    @property
    def provider(self) -> str:
        """Return the configured LLM provider label."""
        return detect_llm_provider(self._base_url)

    async def stream(
        self,
        messages: list[dict[str, str]],
        *,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Yield text deltas from a streaming Gemini interaction."""
        payload = {
            "model": self._model,
            "store": False,
            "input": _format_chat_input(
                messages,
                system_prompt=system_prompt or SYSTEM_PROMPT,
            ),
            "stream": True,
            "generation_config": {
                "temperature": temperature,
                "max_output_tokens": 2048,
            },
        }

        try:
            has_text = False
            async with (
                httpx.AsyncClient(timeout=30.0) as client,
                client.stream(
                    "POST",
                    f"{self._base_url}/interactions?alt=sse",
                    headers=_stream_headers(self._api_key),
                    json=payload,
                ) as response,
            ):
                response.raise_for_status()
                async for line in response.aiter_lines():
                    content = _stream_text_chunk(line)
                    if not content:
                        continue
                    has_text = True
                    yield content
        except httpx.HTTPStatusError as exc:
            raise_gemini_http_error(exc)
        except httpx.TimeoutException:
            logger.warning("Gemini API timeout")
            raise ApiError(504, "Gemini API timed out") from None
        except httpx.HTTPError as exc:
            logger.error("Gemini API connection error", error=exc)
            raise ApiError(502, "Gemini API unreachable") from None

        if not has_text:
            raise ApiError(502, "Gemini returned no response text")

        logger.info("Gemini chat stream completed", context={"model": self._model})
