/** Tile subtitles only for names that do not say what the tool does. */
const TOOL_TILE_HINTS: Readonly<Record<string, string>> = {
  "health-checker": "Check uptime, latency, SSL, and DNS.",
  "data-extract": "Pull rows out of CSV, JSON, and XML.",
  "db-maintenance": "Backup, sync, cleanup, or seed — behind a captcha.",
};

/**
 * One-line task blurbs for the public Tools catalog (`presentation="public"`).
 * Guests need every tile to state the task without opening it.
 */
export const PUBLIC_TOOL_TILE_BLURBS: Readonly<Record<string, string>> = {
  weather: "Check the weather and local time.",
  "url-shortener": "Shorten a long link.",
  recipes: "Open a recipe book and food notes.",
  calculator: "Do a quick calculation.",
  "password-generator": "Create a strong password.",
  "qr-generator": "Make a QR code from text or a link.",
};

/** Optional launcher-tile hint for a platform service slug. */
export function tileHintForSlug(slug: string): string | undefined {
  return TOOL_TILE_HINTS[slug];
}

/** Public Tools tile blurb — prefer the public map, then ambiguous-name hints. */
export function publicTileBlurbForSlug(slug: string): string | undefined {
  return PUBLIC_TOOL_TILE_BLURBS[slug] ?? TOOL_TILE_HINTS[slug];
}
