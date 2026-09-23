"""Feature toggles shared by API and platform catalog.

Public portfolio search (``AI_SEARCH_ENABLED``) and admin AI chat
(``AI_CHAT_ENABLED``) are intentionally independent toggles.
"""

from app.platform.registry import ServiceSlug
from app.settings import get_settings

_UNTRUSTED_URL_TOOL_SLUGS: frozenset[ServiceSlug] = frozenset(
    {
        "vid-download",
        "file-share",
        "health-checker",
    },
)


def is_ai_chat_enabled() -> bool:
    settings = get_settings()
    return settings.AI_CHAT_ENABLED and bool(settings.GROQ_API_KEY.strip())


def is_ai_search_enabled() -> bool:
    settings = get_settings()
    return settings.AI_SEARCH_ENABLED and bool(settings.GROQ_API_KEY)


def is_task_intake_ai_enabled() -> bool:
    settings = get_settings()
    return settings.TASK_INTAKE_AI_ENABLED and bool(settings.GROQ_API_KEY)


def is_expenses_enabled() -> bool:
    """Whether expenses ledger and public calculator are available."""
    return get_settings().EXPENSES_ENABLED


def is_untrusted_url_tools_enabled() -> bool:
    """Whether yt-dlp, file-share, and outbound health-checker are mounted."""
    return get_settings().UNTRUSTED_URL_TOOLS_ENABLED


def is_service_enabled(slug: ServiceSlug) -> bool:
    if slug == "ai-chat":
        return is_ai_chat_enabled()
    if slug == "expenses":
        return is_expenses_enabled()
    if slug in _UNTRUSTED_URL_TOOL_SLUGS:
        return is_untrusted_url_tools_enabled()
    return True
