/** One-line page intros keyed by Vue Router route `name`. */
const TOOL_PAGE_INTROS: Readonly<Record<string, string>> = {
  calculator:
    "Add, subtract, multiply, and divide. The result is computed on the server.",
  "password-generator":
    "Build a random password and choose which character sets to include.",
  "qr-generator": "Make a QR from text or a URL. Sign in to keep a library of codes.",
  recipes: "Save recipes and food notes you can open again later.",
  shortener: "Turn a long link into a short /s/… address you can share.",
  weather: "Look up weather and local time, and keep the places you check often.",
  "vid-download":
    "Download a video with yt-dlp. This tool stays off unless the server enables it.",
  "tool-health-checker": "Watch a site or API for uptime, latency, SSL, and DNS.",
  "tool-tasks": "Tasks and reminders, shared with the Telegram bot and Google Calendar.",
  "tool-expenses": "Log spending, convert currencies, and plan a budget.",
  "tool-file-share": "Upload a file and open it from another device with a short link.",
  "tool-email": "Send a styled email from the admin panel.",
  "tool-feedback": "Read messages visitors sent from the site.",
  "admin-news": "Review the curated news digest before it goes live.",
  "news-sources": "Choose the RSS feeds that fill the public news page.",
  "tool-data-extract": "Turn a CSV, JSON, XML, or delimited file into rows.",
  "tool-audit": "Review security and domain changes recorded by the app.",
  "tool-app-logs": "Browse application log lines saved on the server.",
  "tool-search": "Search admin content that has been indexed.",
  "tool-ai-chat": "Chat with Groq from the admin panel.",
  "tool-db-maintenance": "Run a backup or migration after a captcha check.",
};

/** Tile subtitles only for names that do not say what the tool does. */
const TOOL_TILE_HINTS: Readonly<Record<string, string>> = {
  "health-checker": "Check uptime, latency, SSL, and DNS.",
  "data-extract": "Pull rows out of CSV, JSON, and XML.",
  "db-maintenance": "Backup or migrate, behind a captcha.",
};

/** Page intro for a Vue Router route name, or undefined when none. */
export function introForRoute(routeName: string | symbol | undefined | null): string | undefined {
  if (typeof routeName !== "string") return undefined;
  return TOOL_PAGE_INTROS[routeName];
}

/** Optional launcher-tile hint for a platform service slug. */
export function tileHintForSlug(slug: string): string | undefined {
  return TOOL_TILE_HINTS[slug];
}
