"""Shared Server-Sent Events helpers for streaming API responses."""

import json
from collections.abc import AsyncIterator

from app.core.exceptions import ApiError
from app.core.logging import logger
from app.services.ai_chat import GroqChatService


async def stream_chat_sse(
    llm: GroqChatService,
    messages: list[dict[str, str]],
    *,
    error_context: str,
) -> AsyncIterator[str]:
    """Stream plain LLM chat completion as SSE delta events."""
    try:
        async for delta in llm.stream(messages):
            yield f"data: {json.dumps({'delta': delta})}\n\n"
        yield f"data: {json.dumps({'done': True, 'model': llm.model})}\n\n"
    except ApiError as exc:
        yield f"data: {json.dumps({'error': exc.message})}\n\n"
    except Exception:
        logger.exception(error_context)
        yield f"data: {json.dumps({'error': 'AI chat failed'})}\n\n"
