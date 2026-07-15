import asyncio
import json
from collections.abc import AsyncIterator

import httpx

from app.core.exceptions import ApiError
from app.core.logging import logger

GROQ_API_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MAX_RETRIES = 2
GROQ_429_MAX_RETRY_AFTER = 30
SYSTEM_PROMPT = (
    "You are a concise, helpful assistant embedded in a developer"
    " portfolio admin panel. Keep responses short and technical"
    " unless asked otherwise."
)


def _normalized_base_url(base_url: str) -> str:
    """Return a Groq API base URL without trailing slashes."""
    return (base_url.strip() or GROQ_API_BASE_URL).rstrip("/")


def detect_llm_provider(_base_url: str = "") -> str:
    """Return the configured LLM provider label."""
    return "groq"


def _headers(api_key: str) -> dict[str, str]:
    """Return Groq REST headers."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }


def _stream_headers(api_key: str) -> dict[str, str]:
    """Return Groq REST headers for SSE streaming."""
    return {
        **_headers(api_key),
        "Accept": "text/event-stream",
    }


def _build_messages(
    messages: list[dict[str, str]],
    *,
    system_prompt: str,
) -> list[dict[str, str]]:
    """Convert local chat messages into OpenAI-compatible chat messages."""
    chat_messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
    ]
    for message in messages:
        if message.get("role") == "system":
            continue
        chat_messages.append(
            {
                "role": message.get("role", "user"),
                "content": message.get("content", ""),
            },
        )
    return chat_messages


def _stream_text_chunk(line: str) -> str | None:
    """Extract assistant text from one OpenAI-compatible SSE data line."""
    if not line.startswith("data: "):
        return None
    raw = line.removeprefix("data: ").strip()
    if not raw or raw == "[DONE]":
        return None
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Groq stream returned invalid JSON chunk")
        return None
    if not isinstance(event, dict):
        return None

    choices = event.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    if not isinstance(first, dict):
        return None
    delta = first.get("delta")
    if not isinstance(delta, dict):
        return None
    content = delta.get("content")
    return content if isinstance(content, str) else None


def _retry_after_seconds(response: httpx.Response) -> int | None:
    """Parse Retry-After header as seconds."""
    raw = response.headers.get("Retry-After")
    if not raw:
        return None
    try:
        return max(1, int(raw))
    except ValueError:
        return None


def _should_retry_rate_limit_429(response: httpx.Response) -> bool:
    """Retry 429 only when the provider signals a short transient wait."""
    retry_after = _retry_after_seconds(response)
    return retry_after is not None and retry_after <= GROQ_429_MAX_RETRY_AFTER


def _truncate_response_body(response: httpx.Response, limit: int = 500) -> str:
    """Return a truncated LLM error body for logs."""
    try:
        return response.text[:limit]
    except (httpx.StreamConsumed, UnicodeDecodeError):
        return ""


async def _sleep_for_retry(response: httpx.Response, attempt: int) -> None:
    """Wait before retrying an LLM request after HTTP 429."""
    retry_after = _retry_after_seconds(response)
    delay = retry_after if retry_after is not None else 2**attempt
    await asyncio.sleep(delay)


def _rate_limit_message(response: httpx.Response) -> str:
    """Return a user-facing Groq rate-limit error with optional wait hint."""
    retry_after = _retry_after_seconds(response)
    if retry_after is not None:
        return f"Groq rate limit exceeded — try again in ~{retry_after}s"
    return "Groq rate limit exceeded — try again shortly"


def raise_llm_http_error(exc: httpx.HTTPStatusError) -> None:
    """Map Groq HTTP errors to local API errors."""
    status_code = exc.response.status_code
    if status_code in {401, 403}:
        raise ApiError(502, "Invalid Groq API key") from None
    if status_code == 429:
        logger.warning(
            "Groq rate limit exceeded",
            context={
                "status_code": status_code,
                "retry_after": _retry_after_seconds(exc.response),
                "body": _truncate_response_body(exc.response),
            },
        )
        raise ApiError(429, _rate_limit_message(exc.response)) from None
    if status_code >= 500:
        raise ApiError(502, "Groq API unreachable") from None
    logger.error("Groq API request failed", context={"status_code": status_code})
    raise ApiError(502, "Groq API request failed") from None


class GroqChatService:
    """Async Groq chat client with streaming text output."""

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        base_url: str = GROQ_API_BASE_URL,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = _normalized_base_url(base_url)

    @property
    def model(self) -> str:
        """Return the configured Groq model."""
        return self._model

    @property
    def base_url(self) -> str:
        """Return the configured Groq API base URL."""
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
        """Yield text deltas from a streaming Groq chat completion."""
        payload = {
            "model": self._model,
            "messages": _build_messages(
                messages,
                system_prompt=system_prompt or SYSTEM_PROMPT,
            ),
            "stream": True,
            "temperature": temperature,
            "max_tokens": 2048,
        }

        has_text = False
        max_attempts = GROQ_MAX_RETRIES + 1
        for attempt in range(max_attempts):
            try:
                async with (
                    httpx.AsyncClient(timeout=30.0) as client,
                    client.stream(
                        "POST",
                        f"{self._base_url}/chat/completions",
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
                break
            except httpx.HTTPStatusError as exc:
                if (
                    exc.response.status_code == 429
                    and _should_retry_rate_limit_429(exc.response)
                    and attempt < max_attempts - 1
                ):
                    logger.warning(
                        "Groq rate limit hit; retrying",
                        context={
                            "attempt": attempt + 1,
                            "max_attempts": max_attempts,
                            "retry_after": _retry_after_seconds(exc.response),
                        },
                    )
                    await _sleep_for_retry(exc.response, attempt)
                    continue
                raise_llm_http_error(exc)
            except httpx.TimeoutException:
                logger.warning("Groq API timeout")
                raise ApiError(504, "Groq API timed out") from None
            except httpx.HTTPError as exc:
                logger.error("Groq API connection error", error=exc)
                raise ApiError(502, "Groq API unreachable") from None

        if not has_text:
            raise ApiError(502, "Groq returned no response text")

        logger.info("Groq chat stream completed", context={"model": self._model})
