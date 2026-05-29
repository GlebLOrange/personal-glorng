"""Canonical catalog of platform services exposed in admin and API."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformService:
    slug: str
    name: str
    category: str
    description: str
    api_prefix: str
    admin_route: str
    icon: str
    capabilities: tuple[str, ...]
    external: bool = False


PLATFORM_SERVICES: tuple[PlatformService, ...] = (
    PlatformService(
        slug="tasks",
        name="Tasks",
        category="productivity",
        description="Manage todobot tasks and reminders",
        api_prefix="/tasks",
        admin_route="/admin/tools/tasks",
        icon="☐",
        capabilities=("read", "write", "schedule"),
    ),
    PlatformService(
        slug="email",
        name="Email",
        category="productivity",
        description="Send styled emails",
        api_prefix="/email",
        admin_route="/admin/tools/email",
        icon="✉",
        capabilities=("write",),
    ),
    PlatformService(
        slug="recipes",
        name="Recipes",
        category="content",
        description="Personal recipe book and food notes",
        api_prefix="/recipes",
        admin_route="/admin/tools/recipes",
        icon="◉",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="file-share",
        name="File Share",
        category="content",
        description="Share files between devices",
        api_prefix="/file-share",
        admin_route="/admin/tools/file-share",
        icon="↗",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="url-shortener",
        name="URL Shortener",
        category="content",
        description="Create and manage short URLs",
        api_prefix="/url-shortener",
        admin_route="/admin/tools/url-shortener",
        icon="⟶",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="weather",
        name="Weather",
        category="utilities",
        description="Look up weather for any city",
        api_prefix="/weather",
        admin_route="/admin/tools/weather",
        icon="☀",
        capabilities=("read",),
    ),
    PlatformService(
        slug="calculator",
        name="Calculator",
        category="utilities",
        description="Quick math calculations",
        api_prefix="/calculator",
        admin_route="/admin/tools/calculator",
        icon="⊞",
        capabilities=("read",),
    ),
    PlatformService(
        slug="vid-download",
        name="Video Download",
        category="utilities",
        description="Download videos with yt-dlp",
        api_prefix="/vid-download",
        admin_route="/admin/tools/vid-download",
        icon="▶",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="ai-chat",
        name="AI Chat",
        category="utilities",
        description="Chat with Groq LLMs from the admin panel",
        api_prefix="/ai-chat",
        admin_route="/admin/tools/ai-chat",
        icon="⊛",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="expenses",
        name="Tool Expenses",
        category="operations",
        description="Track SaaS charges and spending charts",
        api_prefix="/expenses",
        admin_route="/admin/tools/expenses",
        icon="¤",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="feedback",
        name="Feedback",
        category="operations",
        description="Read visitor feedback messages",
        api_prefix="/feedback",
        admin_route="/admin/tools/feedback",
        icon="💬",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="audit",
        name="Audit Log",
        category="operations",
        description="Review security and domain change events",
        api_prefix="/audit",
        admin_route="/admin/tools/audit",
        icon="◎",
        capabilities=("read",),
    ),
    PlatformService(
        slug="api-docs",
        name="API Docs",
        category="operations",
        description="Swagger API documentation",
        api_prefix="/docs",
        admin_route="/api/docs",
        icon="❴❵",
        capabilities=("read",),
        external=True,
    ),
)

CATEGORY_LABELS: dict[str, str] = {
    "productivity": "Productivity",
    "content": "Content",
    "utilities": "Utilities",
    "operations": "Operations",
}
