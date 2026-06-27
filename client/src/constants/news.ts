export const NEWS_THEMES = [
  "world",
  "business",
  "tech",
  "security",
  "climate",
  "science",
  "health",
  "culture",
  "politics",
] as const;

export const NEWS_THEME_LIMIT = 4;
export const NEWS_TITLE_MAX_LENGTH = 90;
export const NEWS_SUMMARY_MAX_LENGTH = 600;
export const NEWS_BULLET_MAX_LENGTH = 180;

export const NEWS_THEME_SET = new Set<string>(NEWS_THEMES);
