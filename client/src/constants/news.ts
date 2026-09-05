import type { NewsStatus } from "@/types";

/** Editorial workflow statuses (slug → chip label). */
export const NEWS_STATUS_META: Record<NewsStatus, { label: string; description: string }> = {
  draft: {
    label: "draft",
    description: "still being written",
  },
  pending_review: {
    label: "pending review",
    description: "ready for editorial approval",
  },
  scheduled: {
    label: "scheduled / future",
    description: "approved and queued for publication",
  },
  published: {
    label: "published",
    description: "live and visible",
  },
  private: {
    label: "private",
    description: "visible only to authorized users",
  },
  trash: {
    label: "trash",
    description: "removed, but recoverable for a while",
  },
};

export const NEWS_STATUSES: readonly NewsStatus[] = [
  "draft",
  "pending_review",
  "scheduled",
  "published",
  "private",
  "trash",
] as const;

export function newsStatusLabel(status: NewsStatus | string): string {
  return NEWS_STATUS_META[status as NewsStatus]?.label ?? status;
}

export function newsStatusDescription(status: NewsStatus | string): string {
  return NEWS_STATUS_META[status as NewsStatus]?.description ?? "";
}

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
