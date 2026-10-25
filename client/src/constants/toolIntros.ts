/**
 * Few lowercase words under a tools tile.
 * Public and admin launchers show every entry. Default presentation
 * only shows names that do not say what the tool does.
 */
const TILE_HELP: Readonly<Record<string, string>> = {
  weather: "local weather and time",
  calculator: "quick math",
  "password-generator": "strong passwords",
  "qr-generator": "qr from a link",
  "url-shortener": "short links",
  recipes: "recipes and notes",
  tasks: "tasks and reminders",
  expenses: "track spending",
  "file-share": "share files",
  "vid-download": "save videos",
  "data-extract": "rows from files",
  news: "news digest",
  "news-sources": "rss sources",
  email: "send email",
  "ai-chat": "groq chat",
  "health-checker": "uptime and dns",
  feedback: "visitor messages",
  audit: "security events",
  "app-logs": "app logs",
  search: "admin search",
  "api-docs": "api reference",
  "db-maintenance": "backup and cleanup",
};

const AMBIGUOUS_TILE_SLUGS = new Set(["health-checker", "data-extract", "db-maintenance"]);

/** Optional launcher-tile hint for a platform service slug. */
export function tileHintForSlug(slug: string): string | undefined {
  if (!AMBIGUOUS_TILE_SLUGS.has(slug)) return undefined;
  return TILE_HELP[slug];
}

/** Tools-page tile line — a few lowercase words for a catalog slug. */
export function publicTileBlurbForSlug(slug: string): string | undefined {
  return TILE_HELP[slug];
}
