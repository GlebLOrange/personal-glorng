/** Skill / share-URL helpers for the canonical resume payload. */

const PAREN_RE = /\([^)]*\)/g;
const NON_ALNUM_RE = /[^a-z0-9]+/g;

export function skillId(label: string): string {
  const cleaned = label.toLowerCase().replace(PAREN_RE, "");
  return cleaned.replace(NON_ALNUM_RE, "-").replace(/^-+|-+$/g, "");
}

export type ShareProfileSelection = {
  sections?: string[];
  skills?: string[];
  projects?: string[];
};

/** Deterministic `/profile` path+query (sorted values, fixed param order). */
export function buildShareProfilePath(selection: ShareProfileSelection = {}): string {
  const parts: string[] = [];
  for (const key of ["sections", "skills", "projects"] as const) {
    const values = selection[key] ?? [];
    const cleaned = [...new Set(values.map((value) => value.trim()).filter(Boolean))].sort();
    if (cleaned.length > 0) {
      parts.push(`${key}=${cleaned.join(",")}`);
    }
  }
  return parts.length > 0 ? `/profile?${parts.join("&")}` : "/profile";
}

export function parseShareCsv(raw: unknown): string[] {
  if (typeof raw !== "string" || !raw.trim()) return [];
  return raw
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}
