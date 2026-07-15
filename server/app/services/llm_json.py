"""Groq JSON completion helper."""

import json
from typing import Any

import httpx

from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.text import sanitize_required_text
from app.services.ai_chat import (
    GROQ_API_BASE_URL,
    GROQ_MAX_RETRIES,
    _headers,
    _retry_after_seconds,
    _should_retry_rate_limit_429,
    _sleep_for_retry,
    raise_llm_http_error,
)
from app.settings import get_settings


def _extract_message_content(payload: dict[str, Any]) -> str:
    """Extract generated text from an OpenAI-compatible chat completion."""
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return "{}"
    first = choices[0]
    if not isinstance(first, dict):
        return "{}"
    message = first.get("message")
    if not isinstance(message, dict):
        return "{}"
    content = message.get("content")
    return content if isinstance(content, str) else "{}"


async def complete_json(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    user_content: str,
    temperature: float = 0.0,
    api_base_url: str = GROQ_API_BASE_URL,
) -> dict[str, Any]:
    """Return a parsed JSON object from a Groq chat completion."""
    cleaned = sanitize_required_text(user_content)
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": cleaned},
        ],
        "temperature": temperature,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"},
    }

    max_attempts = GROQ_MAX_RETRIES + 1
    response: httpx.Response | None = None
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{api_base_url.rstrip('/')}/chat/completions",
                    headers=_headers(api_key),
                    json=payload,
                )
                response.raise_for_status()
            break
        except httpx.HTTPStatusError as exc:
            if (
                exc.response.status_code == 429
                and _should_retry_rate_limit_429(exc.response)
                and attempt < max_attempts - 1
            ):
                logger.warning(
                    "Groq rate limit hit; retrying JSON request",
                    context={
                        "attempt": attempt + 1,
                        "max_attempts": max_attempts,
                        "model": model,
                        "retry_after": _retry_after_seconds(exc.response),
                    },
                )
                await _sleep_for_retry(exc.response, attempt)
                continue
            raise_llm_http_error(exc)
        except httpx.TimeoutException:
            logger.warning("LLM JSON timeout", context={"model": model})
            raise ApiError(504, "AI API timed out") from None
        except httpx.HTTPError as exc:
            logger.error("LLM JSON connection error", error=exc)
            raise ApiError(502, "AI API unreachable") from None

    if response is None:
        raise ApiError(502, "AI API unreachable")

    raw = _extract_message_content(response.json())
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
    """Return configured Groq API key, or None if unset."""
    value = get_settings().GROQ_API_KEY
    return value or None
