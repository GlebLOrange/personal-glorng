from dataclasses import dataclass
from typing import Any

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


@dataclass(frozen=True)
class ProviderConfig:
    """Static config for an OpenAI-compatible provider."""

    base_url: str | None
    models: list[str]
    default_model: str
    settings_key: str  # env var field on Settings


# Only DeepSeek is enabled for now; add other providers back here when needed.
PROVIDERS: dict[str, ProviderConfig] = {
    "deepseek": ProviderConfig(
        base_url="https://api.deepseek.com",
        models=["deepseek-chat", "deepseek-reasoner"],
        default_model="deepseek-chat",
        settings_key="DEEPSEEK_API_KEY",
    ),
}


class AIProviderRegistry:
    """Holds API keys and builds OpenAI clients per provider."""

    def __init__(self, api_keys: dict[str, str]) -> None:
        self._keys = {k: v for k, v in api_keys.items() if v}

    def available_providers(self) -> list[dict[str, Any]]:
        """Return providers that have an API key configured."""
        result = []
        for name, cfg in PROVIDERS.items():
            if name not in self._keys:
                continue
            result.append({
                "id": name,
                "models": cfg.models,
                "default_model": cfg.default_model,
            })
        return result

    def build_service(
        self, provider: str, model: str | None = None
    ) -> "OpenAIService":
        """Create an OpenAIService for the given provider."""
        if provider not in PROVIDERS:
            raise ApiError(400, f"Unknown provider: {provider}")
        cfg = PROVIDERS[provider]
        api_key = self._keys.get(provider)
        if not api_key:
            raise ApiError(503, f"{provider} API key is not configured")
        return OpenAIService(
            api_key=api_key,
            model=model or cfg.default_model,
            base_url=cfg.base_url,
        )


class OpenAIService:
    """Async wrapper around an OpenAI-compatible Chat Completions API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
    ) -> None:
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0,
        )
        self._model = model

    async def complete(
        self, messages: list[dict[str, str]]
    ) -> dict[str, Any]:
        """Send a chat completion request."""
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
        ]

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=full_messages,
                max_tokens=2048,
                temperature=0.7,
            )
        except AuthenticationError:
            raise ApiError(502, "Invalid API key") from None
        except RateLimitError:
            raise ApiError(
                429, "Rate limit exceeded — try again shortly"
            ) from None
        except APITimeoutError:
            logger.warning("AI API timeout")
            raise ApiError(504, "AI API timed out") from None
        except APIConnectionError as exc:
            logger.error("AI API connection error", error=exc)
            raise ApiError(502, "AI API unreachable") from None

        choice = response.choices[0].message.content or ""
        usage = response.usage

        logger.info(
            "AI chat completion",
            context={
                "model": response.model,
                "tokens": usage.total_tokens if usage else 0,
            },
        )

        return {
            "reply": choice,
            "model": response.model,
            "usage": {
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0,
            },
        }
