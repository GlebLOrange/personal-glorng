import type { PlatformService } from "@/platform/services";
import { SMALL_TOOL_TABS, SMALL_TOOL_TAB_SLUGS } from "@/constants/smallToolTabs";

/** Tools-page-only section ids — not PlatformService.category. */
export const TOOLS_PAGE_GROUP_ORDER = ["utils", "content", "server"] as const;

export type ToolsPageGroupId = (typeof TOOLS_PAGE_GROUP_ORDER)[number];

export const TOOLS_PAGE_GROUP_LABELS: Record<ToolsPageGroupId, string> = {
  utils: "utils",
  content: "content",
  server: "server",
};

/** Demo chip targets for catalog *tiles* only (utils pills never show chips). */
export const TOOLS_PAGE_DEMO_SLUGS = new Set(["recipes"]);

/** Capability extras that show a "yours" chip when listed as tiles. */
const YOURS_CHIP_SLUGS = new Set([
  "tasks",
  "expenses",
  "file-share",
  "vid-download",
  "data-extract",
]);

/**
 * Utils tools open as standalone PageShell pages. Content and server stay catalog cards.
 * Pinned slugs lead each group; the rest keep their previous relative order.
 */
const SLUG_TO_GROUP: Record<string, ToolsPageGroupId> = {
  weather: "utils",
  calculator: "utils",
  "password-generator": "utils",
  "qr-generator": "utils",
  "url-shortener": "utils",
  "file-share": "utils",
  "data-extract": "utils",
  "vid-download": "utils",
  email: "utils",
  "ai-chat": "utils",
  recipes: "content",
  tasks: "content",
  expenses: "content",
  news: "content",
  "news-sources": "content",
  feedback: "server",
  search: "server",
  "api-docs": "server",
  audit: "server",
  "app-logs": "server",
  "db-maintenance": "server",
  "health-checker": "server",
};

/**
 * Stable order within each tools-page group. Utils order comes from SMALL_TOOL_TABS
 * (single source of truth for the pills); content/server are listed here.
 */
const SLUG_ORDER: Record<string, number> = {
  ...Object.fromEntries(SMALL_TOOL_TABS.map((tab, index) => [tab.id, index])),
  expenses: 0,
  tasks: 1,
  recipes: 2,
  news: 3,
  "news-sources": 4,
  "health-checker": 0,
  "db-maintenance": 1,
  search: 2,
  feedback: 3,
  "api-docs": 4,
  audit: 5,
  "app-logs": 6,
};

export type ToolsPageSection = {
  category: ToolsPageGroupId;
  label: string;
  services: PlatformService[];
};

export function toolsPageGroupForSlug(slug: string): ToolsPageGroupId | undefined {
  return SLUG_TO_GROUP[slug];
}

/** Drop utils-tab peers so they never also appear as content/server tiles. */
export function withoutUtilsTabPeers(services: PlatformService[]): PlatformService[] {
  return services.filter((svc) => !SMALL_TOOL_TAB_SLUGS.has(svc.slug));
}

/** demo = public six; yours = capability extras (tasks, expenses, …). */
export function toolsPageChipForSlug(slug: string): "demo" | "yours" | undefined {
  // Utils spoiler uses tab pills — chips only apply to tile sections.
  if (SMALL_TOOL_TAB_SLUGS.has(slug)) return undefined;
  if (TOOLS_PAGE_DEMO_SLUGS.has(slug)) return "demo";
  if (YOURS_CHIP_SLUGS.has(slug)) return "yours";
  return undefined;
}

/**
 * Group services for /tools only. Does not change PlatformService.category
 * or admin hub grouping via groupServicesByCategory.
 */
export function groupServicesForToolsPage(services: PlatformService[]): ToolsPageSection[] {
  const grouped = new Map<ToolsPageGroupId, PlatformService[]>();
  const seen = new Set<string>();
  for (const svc of services) {
    if (seen.has(svc.slug)) continue;
    seen.add(svc.slug);
    const group = SLUG_TO_GROUP[svc.slug];
    if (!group) continue;
    // Utils-tab peers belong only in the utils group (pills), never content/server tiles.
    if (group !== "utils" && SMALL_TOOL_TAB_SLUGS.has(svc.slug)) continue;
    const list = grouped.get(group) ?? [];
    list.push(svc);
    grouped.set(group, list);
  }
  return TOOLS_PAGE_GROUP_ORDER.filter((id) => grouped.has(id)).map((id) => ({
    category: id,
    label: TOOLS_PAGE_GROUP_LABELS[id],
    services: (grouped.get(id) ?? []).sort(
      (a, b) => (SLUG_ORDER[a.slug] ?? 99) - (SLUG_ORDER[b.slug] ?? 99),
    ),
  }));
}
