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
    public: bool = False


PLATFORM_SERVICES: tuple[PlatformService, ...] = (
    PlatformService(
        slug="tasks",
        name="tasks",
        category="productivity",
        description="Manage todobot tasks and reminders",
        api_prefix="/tasks",
        admin_route="/admin/tools/tasks",
        icon="☐",
        capabilities=("read", "write", "schedule"),
    ),
    PlatformService(
        slug="email",
        name="email",
        category="productivity",
        description="Send styled emails",
        api_prefix="/email",
        admin_route="/admin/tools/email",
        icon="✉",
        capabilities=("write",),
    ),
    PlatformService(
        slug="expenses",
        name="expenses",
        category="productivity",
        description="Monthly personal spending ledger, charts, and currency converter",
        api_prefix="/expenses",
        admin_route="/admin/tools/expenses",
        icon="¤",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="recipes",
        name="recipes",
        category="content",
        description="Personal recipe book and food notes",
        api_prefix="/recipes",
        admin_route="/admin/tools/recipes",
        icon="◉",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="file-share",
        name="file share",
        category="content",
        description="Share files between devices",
        api_prefix="/file-share",
        admin_route="/admin/tools/file-share",
        icon="↗",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="url-shortener",
        name="url shortener",
        category="content",
        description="Create and manage short URLs",
        api_prefix="/url-shortener",
        admin_route="/admin/tools/url-shortener",
        icon="⟶",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="calculator",
        name="calculator",
        category="utilities",
        description="Quick math calculations",
        api_prefix="/calculator",
        admin_route="/calculator",
        icon="⊞",
        capabilities=("read",),
        public=True,
    ),
    PlatformService(
        slug="vid-download",
        name="video download",
        category="utilities",
        description="Download videos with yt-dlp",
        api_prefix="/vid-download",
        admin_route="/admin/tools/vid-download",
        icon="▶",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="ai-chat",
        name="ai chat",
        category="utilities",
        description="Chat with Groq LLMs from the admin panel",
        api_prefix="/ai-chat",
        admin_route="/admin/tools/ai-chat",
        icon="⊛",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="feedback",
        name="feedback",
        category="operations",
        description="Read visitor feedback messages",
        api_prefix="/feedback",
        admin_route="/admin/tools/feedback",
        icon="💬",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="audit",
        name="audit log",
        category="operations",
        description="Review security and domain change events",
        api_prefix="/audit",
        admin_route="/admin/tools/audit",
        icon="◎",
        capabilities=("read",),
    ),
    PlatformService(
        slug="api-docs",
        name="api docs",
        category="operations",
        description="Swagger API documentation",
        api_prefix="/docs",
        admin_route="/api/docs",
        icon="{}",
        capabilities=("read",),
        external=True,
    ),
)

CATEGORY_LABELS: dict[str, str] = {
    "productivity": "productivity",
    "content": "content",
    "utilities": "utilities",
    "operations": "operations",
}
