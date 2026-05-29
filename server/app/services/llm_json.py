"""OpenAI-compatible JSON completion helper."""

import json
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
from app.services.ai_chat import PROVIDERS, sanitize_content


async def complete_json(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    user_content: str,
    base_url: str | None = None,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """Return parsed JSON object from a chat completion."""
    client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=45.0)
    cleaned = sanitize_content(user_content)

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": cleaned},
            ],
            max_tokens=1024,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
    except AuthenticationError:
        raise ApiError(502, "Invalid API key") from None
    except RateLimitError:
        raise ApiError(429, "Rate limit exceeded") from None
    except APITimeoutError:
        logger.warning("LLM JSON timeout", context={"model": model})
        raise ApiError(504, "AI API timed out") from None
    except APIConnectionError as exc:
        logger.error("LLM JSON connection error", error=exc)
        raise ApiError(502, "AI API unreachable") from None

    raw = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned invalid JSON", context={"raw": raw[:500]})
        msg = "AI returned invalid JSON"
        raise ApiError(502, msg) from exc

    if not isinstance(parsed, dict):
        msg = "AI JSON root must be an object"
        raise TypeError(msg)
    return parsed


def groq_api_key() -> str | None:
    key = PROVIDERS["groq"]
    from app.settings import get_settings

    value = getattr(get_settings(), key.settings_key, "")
    return value or None
