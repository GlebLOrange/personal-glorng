/** Tile subtitles only for names that do not say what the tool does. */
const TOOL_TILE_HINTS: Readonly<Record<string, string>> = {
  "health-checker": "Check uptime, latency, SSL, and DNS.",
  "data-extract": "Pull rows out of CSV, JSON, and XML.",
  "db-maintenance": "Backup, sync, cleanup, or seed — behind a captcha.",
};

/** Optional launcher-tile hint for a platform service slug. */
export function tileHintForSlug(slug: string): string | undefined {
  return TOOL_TILE_HINTS[slug];
}
