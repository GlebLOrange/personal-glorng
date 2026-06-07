"""AI chat completions. Default: `ai-chat:read`; streaming: `ai-chat:write`."""

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import AppSettings, OpenAIChatService, require_capability
from app.core.exceptions import ApiError
from app.core.feature_flags import is_ai_chat_enabled
from app.openapi import requires_capability
from app.schemas.ai_chat import ChatConfigResponse, ChatRequest
from app.services.ai_chat import OpenAIService, detect_llm_provider

router = APIRouter(
    prefix="/ai-chat",
    tags=["ai-chat"],
    dependencies=[Depends(require_capability("ai-chat", "read"))],
)


def _require_ai_chat_enabled() -> None:
    if not is_ai_chat_enabled():
        raise ApiError(503, "AI chat is disabled")


@router.get(
    "/config",
    response_model=ChatConfigResponse,
    summary="Read AI chat configuration",
    description=requires_capability("ai-chat", "read"),
)
async def chat_config(settings: AppSettings) -> ChatConfigResponse:
    base_url = settings.LLM_BASE_URL.strip()
    return ChatConfigResponse(
        enabled=is_ai_chat_enabled(),
        configured=bool(settings.OPENAI_API_KEY),
        model=settings.OPENAI_CHAT_MODEL,
        provider=detect_llm_provider(base_url),
        base_url=base_url or None,
    )


async def _sse_events(
    service: OpenAIService,
    messages: list[dict[str, str]],
) -> AsyncIterator[str]:
    try:
        async for delta in service.stream(messages):
            yield f"data: {json.dumps({'delta': delta})}\n\n"
        yield f"data: {json.dumps({'done': True, 'model': service.model})}\n\n"
    except ApiError as exc:
        yield f"data: {json.dumps({'error': exc.message})}\n\n"


@router.post(
    "",
    summary="Stream chat completion",
    description=requires_capability("ai-chat", "write"),
    dependencies=[Depends(require_capability("ai-chat", "write"))],
)
async def chat(body: ChatRequest, service: OpenAIChatService) -> StreamingResponse:
    _require_ai_chat_enabled()
    messages = [m.model_dump() for m in body.messages]
    return StreamingResponse(
        _sse_events(service, messages),
        media_type="text/event-stream",
    )
