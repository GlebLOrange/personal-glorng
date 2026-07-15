"""Canonical catalog of platform services exposed in admin and API."""

from dataclasses import dataclass
from typing import Literal

ServiceSlug = Literal[
    "tasks",
    "email",
    "expenses",
    "news",
    "recipes",
    "file-share",
    "url-shortener",
    "calculator",
    "password-generator",
    "vid-download",
    "ai-chat",
    "data-extract",
    "feedback",
    "news-sources",
    "audit",
    "app-logs",
    "api-docs",
]

Capability = Literal["read", "write", "schedule"]

Category = Literal["productivity", "content", "utilities", "operations"]


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
    public_route: str | None = None


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
        description="Track spending, convert currencies, sum items, and plan budgets",
        api_prefix="/expenses",
        admin_route="/admin/tools/expenses",
        icon="¤",
        capabilities=("read", "write"),
        public=True,
        public_route="/expense-calculator",
    ),
    PlatformService(
        slug="recipes",
        name="recipes",
        category="content",
        description="Personal recipe book and food notes",
        api_prefix="/recipes",
        admin_route="/recipes",
        icon="◉",
        capabilities=("read", "write"),
        public=True,
    ),
    PlatformService(
        slug="news",
        name="news",
        category="content",
        description="Curated worldwide news digest with source attribution",
        api_prefix="/tools/news",
        admin_route="/news",
        icon="◇",
        capabilities=("read", "write"),
        public=True,
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
        admin_route="/shortener",
        icon="⟶",
        capabilities=("read", "write"),
        public=True,
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
        slug="password-generator",
        name="password generator",
        category="utilities",
        description="Generate strong random passwords",
        api_prefix="/password-generator",
        admin_route="/password-generator",
        icon="⚿",
        capabilities=("read",),
        public=True,
    ),
    PlatformService(
        slug="vid-download",
        name="video download",
        category="utilities",
        description="Download videos with yt-dlp",
        api_prefix="/vid-download",
        admin_route="/vid-download",
        icon="▶",
        capabilities=("read", "write"),
        public=True,
    ),
    PlatformService(
        slug="ai-chat",
        name="ai chat",
        category="utilities",
        description="Chat with Groq from the admin panel",
        api_prefix="/ai-chat",
        admin_route="/admin/tools/ai-chat",
        icon="⊛",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="data-extract",
        name="data extract",
        category="utilities",
        description="Extract structured rows from CSV, JSON, XML, and delimited files",
        api_prefix="/data-extract",
        admin_route="/admin/tools/data-extract",
        icon="⎘",
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
        slug="news-sources",
        name="news sources",
        category="content",
        description="Manage RSS sources for the public news page",
        api_prefix="/tools/news-sources",
        admin_route="/admin/tools/news-sources",
        icon="◇",
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
        slug="app-logs",
        name="app logs",
        category="operations",
        description="Browse persisted application log entries",
        api_prefix="/app-logs",
        admin_route="/admin/tools/app-logs",
        icon="≡",
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
