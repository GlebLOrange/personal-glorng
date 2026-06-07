from collections.abc import AsyncIterator
from urllib.parse import urlparse

from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)

from app.core.exceptions import ApiError
from app.core.logging import logger

SYSTEM_PROMPT = (
    "You are a concise, helpful assistant embedded in a developer"
    " portfolio admin panel. Keep responses short and technical"
    " unless asked otherwise."
)


def detect_llm_provider(base_url: str) -> str:
    """Return a short provider label derived from the configured base URL."""
    if not base_url.strip():
        return "openai"

    host = urlparse(base_url.strip()).netloc.lower()
    if "groq.com" in host:
        return "groq"
    if "openrouter.ai" in host:
        return "openrouter"
    if ":11434" in host or host.startswith("127.0.0.1") or host.startswith("localhost"):
        return "ollama"
    if "together" in host:
        return "together"
    return "custom"


class OpenAIService:
    """Async OpenAI-compatible chat completions with streaming."""

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        base_url: str = "",
    ) -> None:
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url.strip() or None,
            timeout=30.0,
        )
        self._model = model
        self._base_url = base_url.strip()

    @property
    def model(self) -> str:
        return self._model

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def provider(self) -> str:
        return detect_llm_provider(self._base_url)

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        """Yield text deltas from a streaming chat completion."""
        user_messages = [m for m in messages if m.get("role") != "system"]
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *user_messages,
        ]

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=full_messages,
                max_tokens=2048,
                temperature=0.7,
                stream=True,
            )
        except AuthenticationError:
            raise ApiError(502, "Invalid API key") from None
        except RateLimitError:
            raise ApiError(429, "Rate limit exceeded — try again shortly") from None
        except APITimeoutError:
            logger.warning("AI API timeout")
            raise ApiError(504, "AI API timed out") from None
        except APIConnectionError as exc:
            logger.error("AI API connection error", error=exc)
            raise ApiError(502, "AI API unreachable") from None

        async for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

        logger.info("AI chat stream completed", context={"model": self._model})
