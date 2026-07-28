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
    "search",
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
        description="manage todobot tasks and reminders",
        api_prefix="/tasks",
        admin_route="/tasks",
        icon="☐",
        capabilities=("read", "write", "schedule"),
    ),
    PlatformService(
        slug="email",
        name="email",
        category="productivity",
        description="send styled emails",
        api_prefix="/email",
        admin_route="/admin/send-email",
        icon="✉",
        capabilities=("write",),
    ),
    PlatformService(
        slug="expenses",
        name="expenses",
        category="productivity",
        description="track spending, convert currencies, sum items, and plan budgets",
        api_prefix="/expenses",
        admin_route="/expenses",
        icon="¤",
        capabilities=("read", "write"),
        public=True,
        public_route="/expense-calculator",
    ),
    PlatformService(
        slug="recipes",
        name="recipes",
        category="content",
        description="personal recipe book and food notes",
        api_prefix="/recipes",
        admin_route="/recipes",
        icon="◉",
        capabilities=("read", "write"),
        public=True,
    ),
    PlatformService(
        slug="news",
        name="manage news",
        category="content",
        description="curated worldwide news digest with source attribution",
        api_prefix="/tools/news",
        admin_route="/admin/news",
        icon="◇",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="file-share",
        name="file share",
        category="content",
        description="share files between devices",
        api_prefix="/file-share",
        admin_route="/file-share",
        icon="↗",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="url-shortener",
        name="url shortener",
        category="content",
        description="create and manage short urls",
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
        description="quick math calculations",
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
        description="generate strong random passwords",
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
        description="download videos with yt-dlp",
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
        description="chat with groq from the admin panel",
        api_prefix="/ai-chat",
        admin_route="/admin/ai-chat",
        icon="⊛",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="data-extract",
        name="data extract",
        category="utilities",
        description="extract structured rows from csv, json, xml, and delimited files",
        api_prefix="/data-extract",
        admin_route="/data-extract",
        icon="⎘",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="feedback",
        name="feedback",
        category="operations",
        description="read visitor feedback messages",
        api_prefix="/feedback",
        admin_route="/admin/feedback",
        icon="💬",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="news-sources",
        name="manage news sources",
        category="content",
        description="manage rss sources for the public news page",
        api_prefix="/tools/news/sources",
        admin_route="/admin/news/sources",
        icon="◇",
        capabilities=("read", "write"),
    ),
    PlatformService(
        slug="audit",
        name="audit logs",
        category="operations",
        description="review security and domain change events",
        api_prefix="/audit",
        admin_route="/admin/audit-logs",
        icon="◎",
        capabilities=("read",),
    ),
    PlatformService(
        slug="app-logs",
        name="app logs",
        category="operations",
        description="browse persisted application log entries",
        api_prefix="/app-logs",
        admin_route="/admin/app-logs",
        icon="≡",
        capabilities=("read",),
    ),
    PlatformService(
        slug="search",
        name="search",
        category="operations",
        description="keyword search across admin indexed content",
        api_prefix="/search",
        admin_route="/admin/search",
        icon="⌕",
        capabilities=("read",),
    ),
    PlatformService(
        slug="api-docs",
        name="api docs",
        category="operations",
        description="swagger api documentation",
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
