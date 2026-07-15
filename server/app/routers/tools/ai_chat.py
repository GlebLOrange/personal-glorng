"""Superuser-only plain AI chat completions."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import AppSettings, GroqChatServiceDep, require_admin
from app.core.exceptions import ApiError
from app.core.feature_flags import is_ai_chat_enabled
from app.core.rate_limit import RateLimiter
from app.routers.sse import stream_chat_sse
from app.schemas.ai_chat import ChatConfigResponse, ChatRequest
from app.services.ai_chat import detect_llm_provider
from app.settings import Settings

router = APIRouter(
    prefix="/ai-chat",
    tags=["ai-chat"],
    dependencies=[Depends(require_admin)],
)

rate_limit_ai_chat = RateLimiter(requests=5, window=300, fail_open=False)


def _require_ai_chat_ready(settings: Settings) -> None:
    if not settings.AI_CHAT_ENABLED:
        raise ApiError(503, "AI chat is disabled")
    if not settings.GROQ_API_KEY.strip():
        raise ApiError(503, "AI chat is not configured")


@router.get(
    "/config",
    response_model=ChatConfigResponse,
    summary="Read AI chat configuration",
)
async def chat_config(settings: AppSettings) -> ChatConfigResponse:
    base_url = settings.GROQ_API_BASE_URL.strip()
    return ChatConfigResponse(
        enabled=is_ai_chat_enabled(),
        configured=bool(settings.GROQ_API_KEY.strip()),
        model=settings.GROQ_CHAT_MODEL,
        provider=detect_llm_provider(base_url),
        base_url=base_url or None,
    )


@router.post(
    "",
    summary="Stream superuser AI chat",
    description="Plain LLM chat for platform superusers only.",
    dependencies=[Depends(rate_limit_ai_chat)],
)
async def chat(
    body: ChatRequest,
    llm: GroqChatServiceDep,
    settings: AppSettings,
) -> StreamingResponse:
    _require_ai_chat_ready(settings)
    messages = [m.model_dump() for m in body.messages]
    return StreamingResponse(
        stream_chat_sse(
            llm,
            messages,
            error_context="Admin AI chat stream failed",
        ),
        media_type="text/event-stream",
    )
