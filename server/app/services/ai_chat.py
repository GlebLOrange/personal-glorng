import re
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
from app.settings import Settings

SYSTEM_PROMPT = (
    "You are a concise, helpful assistant embedded in a developer"
    " portfolio admin panel. Keep responses short and technical"
    " unless asked otherwise."
)

DEFAULT_PROVIDER = "groq"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_content(text: str) -> str:
    """Strip, remove control chars, and reject empty message content."""
    cleaned = _CONTROL_CHAR_RE.sub("", text.strip())
    if not cleaned:
        msg = "Message content must not be empty"
        raise ValueError(msg)
    return cleaned


@dataclass(frozen=True)
class ProviderConfig:
    """Static config for an OpenAI-compatible provider."""

    base_url: str | None
    models: list[str]
    default_model: str
    settings_key: str


PROVIDERS: dict[str, ProviderConfig] = {
    "groq": ProviderConfig(
        base_url="https://api.groq.com/openai/v1",
        models=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
        ],
        default_model=DEFAULT_MODEL,
        settings_key="GROQ_API_KEY",
    ),
}


def build_api_keys(settings: Settings) -> dict[str, str]:
    """Build provider API key map from settings using PROVIDERS config."""
    return {
        name: getattr(settings, cfg.settings_key) for name, cfg in PROVIDERS.items()
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
            result.append(
                {
                    "id": name,
                    "models": cfg.models,
                    "default_model": cfg.default_model,
                }
            )
        return result

    def build_service(self, provider: str, model: str | None = None) -> "OpenAIService":
        """Create an OpenAIService for the given provider."""
        if provider not in PROVIDERS:
            raise ApiError(400, f"Unknown provider: {provider}")
        cfg = PROVIDERS[provider]
        api_key = self._keys.get(provider)
        if not api_key:
            raise ApiError(503, f"{provider} API key is not configured")
        resolved_model = model or cfg.default_model
        if resolved_model not in cfg.models:
            raise ApiError(400, f"Unknown model for {provider}: {resolved_model}")
        return OpenAIService(
            api_key=api_key,
            model=resolved_model,
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

    async def complete(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        """Send a chat completion request."""
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
