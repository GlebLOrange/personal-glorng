from fastapi import APIRouter, Depends

from app.core.deps import AIRegistry, require_admin
from app.core.exceptions import ApiError
from app.core.feature_flags import is_ai_chat_enabled
from app.schemas.ai_chat import ChatRequest, ChatResponse, ProviderInfo

router = APIRouter(prefix="/ai-chat", dependencies=[Depends(require_admin)])


def _require_ai_chat_enabled() -> None:
    if not is_ai_chat_enabled():
        raise ApiError(503, "AI chat is disabled")


@router.get("/providers", response_model=list[ProviderInfo])
async def list_providers(registry: AIRegistry) -> list[ProviderInfo]:
    _require_ai_chat_enabled()
    """Return providers that have an API key configured."""
    return [ProviderInfo(**p) for p in registry.available_providers()]


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest, registry: AIRegistry) -> ChatResponse:
    _require_ai_chat_enabled()
    service = registry.build_service(body.provider, body.model)
    messages = [m.model_dump() for m in body.messages]
    result = await service.complete(messages)
    return ChatResponse(**result)
