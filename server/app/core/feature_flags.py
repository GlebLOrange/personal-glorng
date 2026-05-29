"""Feature toggles shared by API and platform catalog."""

from app.settings import get_settings


def is_ai_chat_enabled() -> bool:
    return get_settings().AI_CHAT_ENABLED


def is_task_intake_ai_enabled() -> bool:
    settings = get_settings()
    return settings.TASK_INTAKE_AI_ENABLED and bool(settings.GROQ_API_KEY)


def is_service_enabled(slug: str) -> bool:
    if slug == "ai-chat":
        return is_ai_chat_enabled()
    return True
