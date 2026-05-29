import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import OpenAIChatService, require_admin
from app.core.exceptions import ApiError
from app.core.feature_flags import is_ai_chat_enabled
from app.schemas.ai_chat import ChatRequest
from app.services.ai_chat import OpenAIService

router = APIRouter(prefix="/ai-chat", dependencies=[Depends(require_admin)])


def _require_ai_chat_enabled() -> None:
    if not is_ai_chat_enabled():
        raise ApiError(503, "AI chat is disabled")


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


@router.post("")
async def chat(body: ChatRequest, service: OpenAIChatService) -> StreamingResponse:
    _require_ai_chat_enabled()
    messages = [m.model_dump() for m in body.messages]
    return StreamingResponse(
        _sse_events(service, messages),
        media_type="text/event-stream",
    )
