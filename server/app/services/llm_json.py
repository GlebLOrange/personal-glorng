"""Gemini JSON completion helper."""

import json
from typing import Any

import httpx

from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.text import sanitize_required_text
from app.services.ai_chat import GEMINI_API_BASE_URL, _headers, raise_gemini_http_error
from app.settings import get_settings

_JSON_OBJECT_SCHEMA = {"type": "object", "additionalProperties": True}


def _extract_output_text(payload: dict[str, Any]) -> str:
    """Extract generated text from a Gemini REST interaction response."""
    output_text = payload.get("output_text")
    if isinstance(output_text, str):
        return output_text

    steps = payload.get("steps")
    if not isinstance(steps, list):
        return "{}"
    for step in reversed(steps):
        if not isinstance(step, dict) or step.get("type") != "model_output":
            continue
        content = step.get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                return item["text"]
    return "{}"


async def complete_json(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    user_content: str,
    temperature: float = 0.0,
    api_base_url: str = GEMINI_API_BASE_URL,
) -> dict[str, Any]:
    """Return a parsed JSON object from a Gemini interaction."""
    cleaned = sanitize_required_text(user_content)
    payload: dict[str, Any] = {
        "model": model,
        "store": False,
        "input": f"{system_prompt}\n\nInput:\n{cleaned}",
        "generation_config": {
            "temperature": temperature,
            "max_output_tokens": 1024,
        },
        "response_format": {
            "type": "text",
            "mime_type": "application/json",
            "schema": _JSON_OBJECT_SCHEMA,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{api_base_url.rstrip('/')}/interactions",
                headers=_headers(api_key),
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise_gemini_http_error(exc)
    except httpx.TimeoutException:
        logger.warning("LLM JSON timeout", context={"model": model})
        raise ApiError(504, "AI API timed out") from None
    except httpx.HTTPError as exc:
        logger.error("LLM JSON connection error", error=exc)
        raise ApiError(502, "AI API unreachable") from None

    raw = _extract_output_text(response.json())
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


def gemini_api_key() -> str | None:
    """Return configured Gemini API key, or None if unset."""
    value = get_settings().GEMINI_API_KEY
    return value or None
