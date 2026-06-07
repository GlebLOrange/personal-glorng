"""Shared Server-Sent Events helpers for streaming API responses."""

import json
from collections.abc import AsyncIterator

from app.core.exceptions import ApiError
from app.core.logging import logger
from app.services.ai_search import AiSearchService, SearchScope


async def stream_search_sse(
    service: AiSearchService,
    messages: list[dict[str, str]],
    *,
    scope: SearchScope,
    error_context: str,
) -> AsyncIterator[str]:
    try:
        async for event in service.stream_events(messages, scope=scope):
            yield f"data: {json.dumps(event)}\n\n"
    except ApiError as exc:
        yield f"data: {json.dumps({'error': exc.message})}\n\n"
    except Exception:
        logger.exception(error_context)
        yield f"data: {json.dumps({'error': 'Search chat failed'})}\n\n"
