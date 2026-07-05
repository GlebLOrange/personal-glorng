export interface PlatformService {
  slug: string;
  name: string;
  category: string;
  categoryLabel: string;
  description: string;
  apiPrefix: string;
  adminRoute: string;
  icon: string;
  capabilities: string[];
  external: boolean;
  public?: boolean;
}

/** Static fallback when API is unavailable; kept in sync with server registry. */
export const PLATFORM_SERVICES: PlatformService[] = [
  {
    slug: "tasks",
    name: "tasks",
    category: "productivity",
    categoryLabel: "productivity",
    description: "Manage todobot tasks and reminders",
    apiPrefix: "/tasks",
    adminRoute: "/admin/tools/tasks",
    icon: "☐",
    capabilities: ["read", "write", "schedule"],
    external: false,
  },
  {
    slug: "email",
    name: "email",
    category: "productivity",
    categoryLabel: "productivity",
    description: "Send styled emails",
    apiPrefix: "/email",
    adminRoute: "/admin/tools/email",
    icon: "✉",
    capabilities: ["write"],
    external: false,
  },
  {
    slug: "expenses",
    name: "expenses",
    category: "productivity",
    categoryLabel: "productivity",
    description: "Monthly personal spending ledger, charts, and currency converter",
    apiPrefix: "/expenses",
    adminRoute: "/admin/tools/expenses",
    icon: "¤",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "recipes",
    name: "recipes",
    category: "content",
    categoryLabel: "content",
    description: "Personal recipe book and food notes",
    apiPrefix: "/recipes",
    adminRoute: "/recipes",
    icon: "◉",
    capabilities: ["read", "write"],
    external: false,
    public: true,
  },
  {
    slug: "news",
    name: "news",
    category: "content",
    categoryLabel: "content",
    description: "Curated worldwide news digest with source attribution",
    apiPrefix: "/tools/news",
    adminRoute: "/news",
    icon: "◇",
    capabilities: ["read", "write"],
    external: false,
    public: true,
  },
  {
    slug: "file-share",
    name: "file share",
    category: "content",
    categoryLabel: "content",
    description: "Share files between devices",
    apiPrefix: "/file-share",
    adminRoute: "/admin/tools/file-share",
    icon: "↗",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "url-shortener",
    name: "url shortener",
    category: "content",
    categoryLabel: "content",
    description: "Create and manage short URLs",
    apiPrefix: "/url-shortener",
    adminRoute: "/shortener",
    icon: "⟶",
    capabilities: ["read", "write"],
    external: false,
    public: true,
  },
  {
    slug: "calculator",
    name: "calculator",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Quick math calculations",
    apiPrefix: "/calculator",
    adminRoute: "/calculator",
    icon: "⊞",
    capabilities: ["read"],
    external: false,
    public: true,
  },
  {
    slug: "password-generator",
    name: "password generator",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Generate strong random passwords",
    apiPrefix: "/password-generator",
    adminRoute: "/password-generator",
    icon: "⚿",
    capabilities: ["read"],
    external: false,
    public: true,
  },
  {
    slug: "vid-download",
    name: "video download",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Download videos with yt-dlp",
    apiPrefix: "/vid-download",
    adminRoute: "/vid-download",
    icon: "▶",
    capabilities: ["read", "write"],
    external: false,
    public: true,
  },
  {
    slug: "weather",
    name: "weather",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Search cities, view local time and weather",
    apiPrefix: "/weather",
    adminRoute: "/weather",
    icon: "◷",
    capabilities: ["read"],
    external: false,
    public: true,
  },
  {
    slug: "ai-chat",
    name: "ai chat",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Chat with Gemini from the admin panel",
    apiPrefix: "/ai-chat",
    adminRoute: "/admin/tools/ai-chat",
    icon: "⊛",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "data-extract",
    name: "data extract",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Extract structured rows from CSV, JSON, XML, and delimited files",
    apiPrefix: "/data-extract",
    adminRoute: "/admin/tools/data-extract",
    icon: "⎘",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "feedback",
    name: "feedback",
    category: "operations",
    categoryLabel: "operations",
    description: "Read visitor feedback messages",
    apiPrefix: "/feedback",
    adminRoute: "/admin/tools/feedback",
    icon: "💬",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "news-sources",
    name: "news sources",
    category: "content",
    categoryLabel: "content",
    description: "Manage RSS sources for the public news page",
    apiPrefix: "/tools/news-sources",
    adminRoute: "/admin/tools/news-sources",
    icon: "◇",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "audit",
    name: "audit log",
    category: "operations",
    categoryLabel: "operations",
    description: "Review security and domain change events",
    apiPrefix: "/audit",
    adminRoute: "/admin/tools/audit",
    icon: "◎",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "app-logs",
    name: "app logs",
    category: "operations",
    categoryLabel: "operations",
    description: "Browse persisted application log entries",
    apiPrefix: "/app-logs",
    adminRoute: "/admin/tools/app-logs",
    icon: "≡",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "api-docs",
    name: "api docs",
    category: "operations",
    categoryLabel: "operations",
    description: "Swagger API documentation",
    apiPrefix: "/docs",
    adminRoute: "/api/docs",
    icon: "❴❵",
    capabilities: ["read"],
    external: true,
  },
];

export interface PlatformCatalog {
  services: PlatformService[];
  categories: Record<string, string>;
}

/** Public tools shown on /tools for guests. */
export function publicToolsAsServices(): PlatformService[] {
  return PLATFORM_SERVICES.filter((s) => s.public);
}

export const PLATFORM_CATEGORIES: Record<string, string> = {
  productivity: "productivity",
  content: "content",
  utilities: "utilities",
  operations: "operations",
};

export function groupServicesByCategory(
  services: PlatformService[],
): { category: string; label: string; services: PlatformService[] }[] {
  const order = Object.keys(PLATFORM_CATEGORIES);
  const grouped = new Map<string, PlatformService[]>();
  for (const svc of services) {
    const list = grouped.get(svc.category) ?? [];
    list.push(svc);
    grouped.set(svc.category, list);
  }
  return order
    .filter((cat) => grouped.has(cat))
    .map((cat) => ({
      category: cat,
      label: PLATFORM_CATEGORIES[cat] ?? cat,
      services: grouped.get(cat)!,
    }));
}
