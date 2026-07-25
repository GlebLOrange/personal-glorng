import { statusBadgeClass } from "@/constants/taskStatus";

/** Neutral styling for unfiltered / "all" chips and tiles. */
export const FILTER_CHIP_NEUTRAL = "text-surface-light bg-surface-dark";

/** Pale 1xx–5xx + muted/neutral — product chips only (no golden/violet). */
const SEMANTIC = {
  info: "text-accent-blue bg-accent-blue/10 border-accent-blue/30",
  success: "text-status-success bg-status-success/10 border-status-success/30",
  warning: "text-status-cyan bg-status-cyan/10 border-status-cyan/30",
  error: "text-status-error bg-status-error/10 border-status-error/30",
  critical: "text-status-critical bg-status-critical/10 border-status-critical/30",
  muted: "text-surface-mid bg-surface-mid/10 border-surface-border",
  neutral: "bg-surface-border text-surface-mid border-surface-border",
} as const;

const NEWS_STATUS_CLASS: Record<string, string> = {
  draft: SEMANTIC.info,
  published: SEMANTIC.success,
  unpublished: SEMANTIC.warning,
  failed: SEMANTIC.error,
};

const FEEDBACK_STATUS_CLASS: Record<string, string> = {
  unread: SEMANTIC.info,
  read: SEMANTIC.muted,
  archived: SEMANTIC.warning,
};

const USER_STATUS_CLASS: Record<string, string> = {
  verified: "bg-status-cyan/15 text-status-cyan border-status-cyan/30",
  unverified: SEMANTIC.neutral,
  protected: "bg-accent-blue/15 text-accent-blue border-accent-blue/30",
};

const USER_ROLE_CLASS: Record<string, string> = {
  superuser: "bg-status-critical/15 text-status-critical border-status-critical/30",
  custom: "bg-surface-dark text-surface-mid border-surface-border",
};

const AUDIT_CATEGORY_CLASS: Record<string, string> = {
  security: SEMANTIC.success,
  domain: SEMANTIC.info,
};

const LOG_LEVEL_CLASS: Record<string, string> = {
  error: SEMANTIC.error,
  warning: SEMANTIC.warning,
  debug: SEMANTIC.neutral,
  info: SEMANTIC.info,
};

function lookupClass(map: Record<string, string>, value: string): string {
  return map[value] ?? SEMANTIC.muted;
}

/** Tailwind classes for news article status chips and badges. */
export function newsStatusClass(status: string): string {
  return lookupClass(NEWS_STATUS_CLASS, status);
}

/** Tailwind classes for feedback status chips and badges. */
export function feedbackStatusClass(status: string): string {
  return lookupClass(FEEDBACK_STATUS_CLASS, status);
}

/** Tailwind classes for user verification status filter chips. */
export function userStatusClass(status: string): string {
  return lookupClass(USER_STATUS_CLASS, status);
}

/** Tailwind classes for user role filter chips. */
export function userRoleClass(role: string): string {
  return lookupClass(USER_ROLE_CLASS, role);
}

/** Tailwind classes for audit category chips and badges. */
export function auditCategoryClass(category: string): string {
  return lookupClass(AUDIT_CATEGORY_CLASS, category);
}

/** Tailwind classes for app log level chips and badges. */
export function logLevelClass(level: string): string {
  return lookupClass(LOG_LEVEL_CLASS, level);
}

/** Tailwind classes for news source enabled/disabled chips and badges. */
export function newsSourceEnabledClass(enabled: boolean): string {
  return enabled ? SEMANTIC.info : SEMANTIC.neutral;
}

/** Re-export task status badge classes for filter chips. */
export { statusBadgeClass };
