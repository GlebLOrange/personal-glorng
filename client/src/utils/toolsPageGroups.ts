import type { PlatformService } from "@/platform/services";

/** Tools-page-only section ids — not PlatformService.category. */
export const TOOLS_PAGE_GROUP_ORDER = [
  "everyday",
  "content",
  "work",
  "builders",
] as const;

export type ToolsPageGroupId = (typeof TOOLS_PAGE_GROUP_ORDER)[number];

export const TOOLS_PAGE_GROUP_LABELS: Record<ToolsPageGroupId, string> = {
  everyday: "Everyday",
  content: "Content",
  work: "Work",
  builders: "Builders",
};

/** Six public demo tools — chip targets on /tools. */
export const TOOLS_PAGE_DEMO_SLUGS = new Set([
  "weather",
  "calculator",
  "password-generator",
  "qr-generator",
  "url-shortener",
  "recipes",
]);

const SLUG_TO_GROUP: Record<string, ToolsPageGroupId> = {
  weather: "everyday",
  calculator: "everyday",
  "password-generator": "everyday",
  "qr-generator": "everyday",
  "url-shortener": "content",
  recipes: "content",
  tasks: "work",
  expenses: "work",
  "file-share": "work",
  "vid-download": "builders",
  "data-extract": "builders",
};

/** Stable order within each tools-page group. */
const SLUG_ORDER: Record<string, number> = {
  weather: 0,
  calculator: 1,
  "password-generator": 2,
  "qr-generator": 3,
  "url-shortener": 0,
  recipes: 1,
  tasks: 0,
  expenses: 1,
  "file-share": 2,
  "vid-download": 0,
  "data-extract": 1,
};

export type ToolsPageSection = {
  category: ToolsPageGroupId;
  label: string;
  services: PlatformService[];
};

export function toolsPageGroupForSlug(slug: string): ToolsPageGroupId | undefined {
  return SLUG_TO_GROUP[slug];
}

/** demo = public six; yours = Work / Builders personal tools. */
export function toolsPageChipForSlug(slug: string): "demo" | "yours" | undefined {
  if (TOOLS_PAGE_DEMO_SLUGS.has(slug)) return "demo";
  const group = SLUG_TO_GROUP[slug];
  if (group === "work" || group === "builders") return "yours";
  return undefined;
}

/**
 * Group services for /tools only. Does not change PlatformService.category
 * or admin hub grouping via groupServicesByCategory.
 */
export function groupServicesForToolsPage(services: PlatformService[]): ToolsPageSection[] {
  const grouped = new Map<ToolsPageGroupId, PlatformService[]>();
  for (const svc of services) {
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
