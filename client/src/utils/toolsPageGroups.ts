import type { PlatformService } from "@/platform/services";
import { SMALL_TOOL_TAB_SLUGS } from "@/constants/smallToolTabs";

/** Tools-page-only section ids — not PlatformService.category. */
export const TOOLS_PAGE_GROUP_ORDER = ["utils", "content", "server"] as const;

export type ToolsPageGroupId = (typeof TOOLS_PAGE_GROUP_ORDER)[number];

export const TOOLS_PAGE_GROUP_LABELS: Record<ToolsPageGroupId, string> = {
  utils: "utils",
  content: "content",
  server: "server",
};

/** Six public demo tools — chip targets on the Tools catalog (tiles only). */
export const TOOLS_PAGE_DEMO_SLUGS = new Set([
  "weather",
  "calculator",
  "password-generator",
  "qr-generator",
  "url-shortener",
  "recipes",
]);

/** Capability extras that show a "yours" chip when listed as tiles. */
const YOURS_CHIP_SLUGS = new Set([
  "tasks",
  "expenses",
  "file-share",
  "vid-download",
  "data-extract",
]);

/**
 * Utils = small-window tab peers (weather / calc / password / QR) plus
 * utility tiles (url-shortener, file-share, data-extract, vid-download, email, ai-chat).
 * Content keeps recipes / tasks / expenses / news; server is ops + health-checker.
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

/** Stable order within each tools-page group. */
const SLUG_ORDER: Record<string, number> = {
  weather: 0,
  calculator: 1,
  "password-generator": 2,
  "qr-generator": 3,
  "url-shortener": 4,
  "file-share": 5,
  "data-extract": 6,
  "vid-download": 7,
  email: 8,
  "ai-chat": 9,
  recipes: 0,
  tasks: 1,
  expenses: 2,
  news: 3,
  "news-sources": 4,
  feedback: 0,
  search: 1,
  "api-docs": 2,
  audit: 3,
  "app-logs": 4,
  "db-maintenance": 5,
  "health-checker": 6,
};

export type ToolsPageSection = {
  category: ToolsPageGroupId;
  label: string;
  services: PlatformService[];
};

export function toolsPageGroupForSlug(slug: string): ToolsPageGroupId | undefined {
  return SLUG_TO_GROUP[slug];
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
