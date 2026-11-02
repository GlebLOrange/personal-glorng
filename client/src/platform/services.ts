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
  publicRoute?: string;
}

/** /admin hub sections. Labels are sentence case; slugs are the tile order. */
const ADMIN_HUB_SECTIONS = [
  { category: "content", label: "Content", slugs: ["news", "news-sources"] },
  { category: "productivity", label: "Productivity", slugs: ["email", "tasks"] },
  {
    category: "utilities",
    label: "Utilities",
    slugs: ["ai-chat", "url-shortener", "weather", "recipes", "health-checker"],
  },
  {
    category: "operations",
    label: "Operations",
    slugs: ["feedback", "audit", "app-logs", "search", "api-docs", "db-maintenance"],
  },
] as const;

/** Tiles shown on /admin, in hub section order. */
export const ADMIN_HUB_SERVICE_SLUGS = new Set<string>(
  ADMIN_HUB_SECTIONS.flatMap((section) => [...section.slugs]),
);

/** Sample tools that show a Demo chip on /admin. */
export const ADMIN_HUB_DEMO_SLUGS = new Set<string>(["ai-chat", "url-shortener", "weather"]);

/** Capability tools listed on /tools for signed-in users (alongside public tools). */
export const TOOLS_PAGE_EXTRA_SLUGS = new Set([
  "tasks",
  "expenses",
  "file-share",
  "data-extract",
  "vid-download",
]);

/** Static fallback when API is unavailable; kept in sync with server registry. */
export const PLATFORM_SERVICES: PlatformService[] = [
  {
    slug: "tasks",
    name: "tasks",
    category: "productivity",
    categoryLabel: "productivity",
    description: "manage todobot tasks and reminders",
    apiPrefix: "/tasks",
    adminRoute: "/tasks",
    icon: "",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "email",
    name: "email",
    category: "productivity",
    categoryLabel: "productivity",
    description: "send styled emails",
    apiPrefix: "/email",
    adminRoute: "/tools/send-email",
    icon: "",
    capabilities: ["write"],
    external: false,
  },
  {
    slug: "expenses",
    name: "expenses",
    category: "productivity",
    categoryLabel: "productivity",
    description: "track spending, convert currencies, sum items, and plan budgets",
    apiPrefix: "/expenses",
    adminRoute: "/expenses",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "news",
    name: "manage news",
    category: "content",
    categoryLabel: "content",
    description: "curated worldwide news digest with source attribution",
    apiPrefix: "/tools/news",
    adminRoute: "/admin/news",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "url-shortener",
    name: "url shortener",
    category: "content",
    categoryLabel: "content",
    description: "create and manage short urls",
    apiPrefix: "/url-shortener",
    adminRoute: "/shortener",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
    public: true,
  },
  {
    slug: "recipes",
    name: "recipes",
    category: "content",
    categoryLabel: "content",
    description: "personal recipe book and food notes",
    apiPrefix: "/recipes",
    adminRoute: "/recipes",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
    public: true,
  },
  {
    slug: "file-share",
    name: "file share",
    category: "content",
    categoryLabel: "content",
    description: "share files between devices",
    apiPrefix: "/file-share",
    adminRoute: "/file-share",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "weather",
    name: "weather",
    category: "utilities",
    categoryLabel: "utilities",
    description: "weather lookup, saved locations, and local time",
    apiPrefix: "/weather",
    adminRoute: "/weather",
    icon: "",
    capabilities: ["read"],
    external: false,
    public: true,
  },
  {
    slug: "calculator",
    name: "calculator",
    category: "utilities",
    categoryLabel: "utilities",
    description: "quick math calculations",
    apiPrefix: "/calculator",
    adminRoute: "/calculator",
    icon: "",
    capabilities: ["read"],
    external: false,
    public: true,
  },
  {
    slug: "password-generator",
    name: "password generator",
    category: "utilities",
    categoryLabel: "utilities",
    description: "generate strong random passwords",
    apiPrefix: "/password-generator",
    adminRoute: "/password-generator",
    icon: "",
    capabilities: ["read"],
    external: false,
    public: true,
  },
  {
    slug: "qr-generator",
    name: "qr generator",
    category: "utilities",
    categoryLabel: "utilities",
    description: "generate qr codes; save and list your own library",
    apiPrefix: "/qr-generator",
    adminRoute: "/qr-generator",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
    public: true,
  },
  {
    slug: "vid-download",
    name: "video downloader",
    category: "utilities",
    categoryLabel: "utilities",
    description: "download videos with yt-dlp",
    apiPrefix: "/vid-download",
    adminRoute: "/vid-download",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "ai-chat",
    name: "ai chat",
    category: "utilities",
    categoryLabel: "utilities",
    description: "chat with groq from the admin panel",
    apiPrefix: "/ai-chat",
    adminRoute: "/admin/ai-chat",
    icon: "",
    capabilities: [],
    external: false,
  },
  {
    slug: "data-extract",
    name: "data extract",
    category: "utilities",
    categoryLabel: "utilities",
    description: "extract structured rows from csv, json, xml, and delimited files",
    apiPrefix: "/data-extract",
    adminRoute: "/data-extract",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "health-checker",
    name: "health checker",
    category: "utilities",
    categoryLabel: "utilities",
    description: "monitor website and api uptime, latency, ssl, and dns",
    apiPrefix: "/health-checker",
    adminRoute: "/health-checker",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "feedback",
    name: "feedback",
    category: "operations",
    categoryLabel: "operations",
    description: "read visitor feedback messages",
    apiPrefix: "/feedback",
    adminRoute: "/admin/feedback",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "news-sources",
    name: "manage news sources",
    category: "content",
    categoryLabel: "content",
    description: "manage rss sources for the public news page",
    apiPrefix: "/tools/news/sources",
    adminRoute: "/admin/news/sources",
    icon: "",
    capabilities: ["read", "write"],
    external: false,
  },
  {
    slug: "audit",
    name: "audit logs",
    category: "operations",
    categoryLabel: "operations",
    description: "review security and domain change events",
    apiPrefix: "/audit",
    adminRoute: "/admin/audit-logs",
    icon: "",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "app-logs",
    name: "app logs",
    category: "operations",
    categoryLabel: "operations",
    description: "browse persisted application log entries",
    apiPrefix: "/app-logs",
    adminRoute: "/admin/app-logs",
    icon: "",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "search",
    name: "search",
    category: "operations",
    categoryLabel: "operations",
    description: "keyword search across admin indexed content",
    apiPrefix: "/search",
    adminRoute: "/admin/search",
    icon: "",
    capabilities: ["read"],
    external: false,
  },
  {
    slug: "api-docs",
    name: "api docs",
    category: "operations",
    categoryLabel: "operations",
    description: "swagger api documentation",
    apiPrefix: "/docs",
    adminRoute: "/api/docs",
    icon: "",
    capabilities: ["read"],
    external: true,
  },
  {
    slug: "db-maintenance",
    name: "db maintenance",
    category: "operations",
    categoryLabel: "operations",
    description: "backup, sync, cleanup, or seed with a captcha gate",
    apiPrefix: "/admin/maintenance",
    adminRoute: "/admin/db-maintenance",
    icon: "",
    capabilities: [],
    external: false,
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

/** Resolve tile link: public route for guests, admin route when user has read access. */
export function resolveToolRoute(
  tool: PlatformService,
  canRead: (slug: string) => boolean,
): string {
  if (tool.publicRoute && !canRead(tool.slug)) {
    return tool.publicRoute;
  }
  return tool.adminRoute;
}

export const PLATFORM_CATEGORIES: Record<string, string> = {
  content: "content",
  productivity: "productivity",
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

export type AdminHubSection = {
  category: string;
  label: string;
  services: PlatformService[];
};

/**
 * Group /admin tiles into Content, Productivity, Utilities, then Operations.
 * Omits empty sections. Does not change PlatformService.category.
 */
export function groupAdminHub(services: PlatformService[]): AdminHubSection[] {
  const bySlug = new Map(services.map((service) => [service.slug, service]));
  const sections: AdminHubSection[] = [];
  for (const section of ADMIN_HUB_SECTIONS) {
    const grouped: PlatformService[] = [];
    for (const slug of section.slugs) {
      const service = bySlug.get(slug);
      if (service) grouped.push(service);
    }
    if (grouped.length === 0) continue;
    sections.push({
      category: section.category,
      label: section.label,
      services: grouped,
    });
  }
  return sections;
}
