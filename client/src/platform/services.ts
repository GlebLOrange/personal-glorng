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
    name: "Tasks",
    category: "productivity",
    categoryLabel: "Productivity",
    description: "Manage todobot tasks and reminders",
    apiPrefix: "/tasks",
    adminRoute: "/admin/tools/tasks",
    icon: "☐",
    capabilities: ["read", "write", "schedule"],
    external: false,
  },
  {
    slug: "email",
    name: "Email",
    category: "productivity",
    categoryLabel: "Productivity",
    description: "Send styled emails",
    apiPrefix: "/email",
    adminRoute: "/admin/tools/email",
    icon: "✉",
    capabilities: ["write"],
    external: false,
  },
  {
    slug: "expenses",
    name: "Expenses",
    category: "productivity",
    categoryLabel: "Productivity",
    description: "Monthly personal spending ledger with charts",
    apiPrefix: "/expenses",
    adminRoute: "/admin/tools/expenses",
    icon: "¤",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "recipes",
    name: "Recipes",
    category: "content",
    categoryLabel: "Content",
    description: "Personal recipe book and food notes",
    apiPrefix: "/recipes",
    adminRoute: "/admin/tools/recipes",
    icon: "◉",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "file-share",
    name: "File Share",
    category: "content",
    categoryLabel: "Content",
    description: "Share files between devices",
    apiPrefix: "/file-share",
    adminRoute: "/admin/tools/file-share",
    icon: "↗",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "url-shortener",
    name: "URL Shortener",
    category: "content",
    categoryLabel: "Content",
    description: "Create and manage short URLs",
    apiPrefix: "/url-shortener",
    adminRoute: "/admin/tools/url-shortener",
    icon: "⟶",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "calculator",
    name: "Calculator",
    category: "utilities",
    categoryLabel: "Utilities",
    description: "Quick math calculations",
    apiPrefix: "/calculator",
    adminRoute: "/admin/tools/calculator",
    icon: "⊞",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "currency",
    name: "Currency Converter",
    category: "utilities",
    categoryLabel: "Utilities",
    description: "Convert between EUR, USD, PLN, and BYN",
    apiPrefix: "/currency",
    adminRoute: "/admin/tools/currency",
    icon: "⇄",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "vid-download",
    name: "Video Download",
    category: "utilities",
    categoryLabel: "Utilities",
    description: "Download videos with yt-dlp",
    apiPrefix: "/vid-download",
    adminRoute: "/admin/tools/vid-download",
    icon: "▶",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "ai-chat",
    name: "AI Chat",
    category: "utilities",
    categoryLabel: "Utilities",
    description: "Chat with Groq LLMs from the admin panel",
    apiPrefix: "/ai-chat",
    adminRoute: "/admin/tools/ai-chat",
    icon: "⊛",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "feedback",
    name: "Feedback",
    category: "operations",
    categoryLabel: "Operations",
    description: "Read visitor feedback messages",
    apiPrefix: "/feedback",
    adminRoute: "/admin/tools/feedback",
    icon: "💬",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "audit",
    name: "Audit Log",
    category: "operations",
    categoryLabel: "Operations",
    description: "Review security and domain change events",
    apiPrefix: "/audit",
    adminRoute: "/admin/tools/audit",
    icon: "◎",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "api-docs",
    name: "API Docs",
    category: "operations",
    categoryLabel: "Operations",
    description: "Swagger API documentation",
    apiPrefix: "/docs",
    adminRoute: "/api/docs",
    icon: "❴❵",
    capabilities: ["read"],
    external: true,
  },
];

export const PLATFORM_CATEGORIES: Record<string, string> = {
  productivity: "Productivity",
  content: "Content",
  utilities: "Utilities",
  operations: "Operations",
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
