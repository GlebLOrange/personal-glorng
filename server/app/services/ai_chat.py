from collections.abc import AsyncIterator

from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)

from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.text import sanitize_text

SYSTEM_PROMPT = (
    "You are a concise, helpful assistant embedded in a developer"
    " portfolio admin panel. Keep responses short and technical"
    " unless asked otherwise."
)


def sanitize_content(text: str) -> str:
    """Strip, remove control chars, and reject empty message content."""
    cleaned = sanitize_text(text)
    if not cleaned:
        msg = "Message content must not be empty"
        raise ValueError(msg)
    return cleaned


class OpenAIService:
    """Async OpenAI chat completions with streaming."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key, timeout=30.0)
        self._model = model

    @property
    def model(self) -> str:
        return self._model

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
