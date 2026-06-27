import type { NewsSource } from "@/types";

const SOURCE_ALIASES: Record<string, string> = {
  dw: "Deutsche Welle",
  nyt: "New York Times",
  nytimes: "New York Times",
};

export function humanTitleFromSlug(slug: string): string | null {
  let decodedSlug = slug;
  try {
    decodedSlug = decodeURIComponent(slug);
  } catch {
    // Keep typing resilient for partially pasted URLs with malformed escapes.
  }
  const words = decodedSlug
    .replace(/[-_]+/g, " ")
    .replace(/[^a-zA-Z0-9]+/g, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  if (words.length === 0) return null;
  return words.map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(" ");
}

export function sourceNameFromSlug(slug: string): string | null {
  const alias = SOURCE_ALIASES[slug.toLowerCase().replace(/[^a-z0-9]+/g, "")];
  if (alias) return alias;
  const title = humanTitleFromSlug(slug);
  if (!title) return null;
  return title
    .split(/\s+/)
    .map((word) => (word.length <= 3 ? word.toUpperCase() : word))
    .join(" ");
}

export function sourceFromMarkedUrl(url: string): string | null {
  const host = url.replace(/^[a-z][a-z0-9+.-]*:\/\//i, "").split(/[/?#]/)[0] ?? "";
  const marker = host.match(/(?:^|\.)\{\{([^{}]+)\}\}(?=\.|(?::\d+)?$)/i);
  return marker ? sourceNameFromSlug(marker[1]) : null;
}

export function sanitizeNewsLink(link: string): string {
  return link.replace(/\{\{([^{}]+)\}\}/g, (_, slug: string) => slug.trim());
}

export function titleFromNewsLink(link: string): string | null {
  const linkWithoutHostMarker = withoutHostSourceMarker(link);
  const marker = linkWithoutHostMarker.match(/\{\{([^{}]+)\}\}/);
  if (marker) return humanTitleFromSlug(marker[1]);
  const dwSlug = link.match(/\/en\/([^/?#]+)\/a-\d+/);
  if (dwSlug) return humanTitleFromSlug(dwSlug[1]);
  const path = link.replace(/^[a-z][a-z0-9+.-]*:\/\/[^/?#]*/i, "").split(/[?#]/)[0];
  const slug = path
    .split("/")
    .filter(Boolean)
    .at(-1)
    ?.replace(/\.[a-z0-9]+$/i, "");
  if (slug) return humanTitleFromSlug(slug);
  try {
    const host = new URL(link).hostname.replace(/^www\./i, "");
    return humanTitleFromSlug(host.split(".")[0] ?? "");
  } catch {
    return null;
  }
}

export function sourceFromNewsLink(link: string, availableSources: NewsSource[]): string | null {
  const sourceName = sourceFromMarkedUrl(link);
  if (!sourceName) return null;
  const sourceNameKey = sourceKey(sourceName);
  return (
    availableSources.find((source) => sourceKey(source.name) === sourceNameKey)?.name ?? sourceName
  );
}

export function normalizeHttpUrl(value: string): string | null {
  const trimmed = sanitizeNewsLink(value.trim());
  try {
    const parsed = new URL(trimmed);
    if (!["http:", "https:"].includes(parsed.protocol)) return null;
    return trimmed;
  } catch {
    return null;
  }
}

function sourceKey(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "");
}

function withoutHostSourceMarker(link: string): string {
  const match = link.match(/^([a-z][a-z0-9+.-]*:\/\/)?([^/?#]*)(.*)$/i);
  if (!match) return link;
  const host = match[2].replace(/(?:^|\.)\{\{([^{}]+)\}\}(?=\.|(?::\d+)?$)/i, "");
  return `${match[1] ?? ""}${host}${match[3] ?? ""}`;
}
