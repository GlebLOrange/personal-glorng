import type { NewsStatus } from "@/types";

export const NEWS_STATUSES: readonly NewsStatus[] = [
  "draft",
  "published",
  "unpublished",
  "failed",
] as const;

export const NEWS_TAGS = [
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

export const NEWS_TAG_LIMIT = 4;
export const NEWS_TITLE_MAX_LENGTH = 90;
export const NEWS_SUMMARY_MAX_LENGTH = 600;
export const NEWS_BULLET_MAX_LENGTH = 180;

export const NEWS_TAG_SET = new Set<string>(NEWS_TAGS);
