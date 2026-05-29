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
}

export interface PlatformCatalog {
  services: PlatformService[];
  categories: Record<string, string>;
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
    description: "Monthly personal spending ledger with charts",
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
    adminRoute: "/admin/tools/recipes",
    icon: "◉",
    capabilities: ["read", "write"],
    external: false,
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
    adminRoute: "/admin/tools/url-shortener",
    icon: "⟶",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "calculator",
    name: "calculator",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Quick math calculations",
    apiPrefix: "/calculator",
    adminRoute: "/admin/tools/calculator",
    icon: "⊞",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "weather",
    name: "weather",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Current weather for a city",
    apiPrefix: "/weather",
    adminRoute: "/admin/tools/weather",
    icon: "☀",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "currency",
    name: "currency converter",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Convert between EUR, USD, PLN, and BYN",
    apiPrefix: "/currency",
    adminRoute: "/admin/tools/currency",
    icon: "⇄",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "vid-download",
    name: "video download",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Download videos with yt-dlp",
    apiPrefix: "/vid-download",
    adminRoute: "/admin/tools/vid-download",
    icon: "▶",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "ai-chat",
    name: "ai chat",
    category: "utilities",
    categoryLabel: "utilities",
    description: "Chat with Groq LLMs from the admin panel",
    apiPrefix: "/ai-chat",
    adminRoute: "/admin/tools/ai-chat",
    icon: "⊛",
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
