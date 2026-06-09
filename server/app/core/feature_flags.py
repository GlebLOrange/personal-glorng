"""Feature toggles shared by API and platform catalog.

Public portfolio search (``AI_SEARCH_ENABLED``) and admin AI chat
(``AI_CHAT_ENABLED``) are intentionally independent toggles.
"""

from app.platform.registry import ServiceSlug
from app.settings import get_settings


def is_ai_chat_enabled() -> bool:
    return get_settings().AI_CHAT_ENABLED


def is_ai_search_enabled() -> bool:
    settings = get_settings()
    return settings.AI_SEARCH_ENABLED and bool(settings.OPENAI_API_KEY)


def is_task_intake_ai_enabled() -> bool:
    settings = get_settings()
    return settings.TASK_INTAKE_AI_ENABLED and bool(settings.OPENAI_API_KEY)


def is_service_enabled(slug: ServiceSlug) -> bool:
    if slug == "ai-chat":
        return is_ai_chat_enabled()
    return True
