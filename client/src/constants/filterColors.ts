import { statusBadgeClass } from "@/constants/taskStatus";

/** Neutral styling for unfiltered / "all" chips and tiles. */
export const FILTER_CHIP_NEUTRAL = "text-surface-light bg-surface-dark";

const SEMANTIC = {
  success: "text-status-success bg-status-success/10 border-status-success/30",
  warning: "text-status-warning bg-status-warning/10 border-status-warning/30",
  error: "text-status-error bg-status-error/10 border-status-error/30",
  info: "text-accent-blue bg-accent-blue/10 border-accent-blue/30",
  golden: "text-accent-golden bg-accent-golden/10 border-accent-golden/30",
  violet: "text-accent-violet bg-accent-violet/10 border-accent-violet/30",
  muted: "text-surface-mid bg-surface-mid/10 border-surface-border",
  neutral: "bg-surface-border text-surface-mid border-surface-border",
  security: "bg-accent-red/20 text-accent-red border-accent-red/30",
  amber: "bg-accent-amber/20 text-accent-amber border-accent-amber/30",
} as const;

const NEWS_STATUS_CLASS: Record<string, string> = {
  draft: SEMANTIC.info,
  published: SEMANTIC.success,
  unpublished: SEMANTIC.golden,
  failed: SEMANTIC.error,
};

const FEEDBACK_STATUS_CLASS: Record<string, string> = {
  unread: SEMANTIC.info,
  read: SEMANTIC.neutral,
  archived: "bg-surface-dark text-surface-muted border-surface-border",
};

const USER_STATUS_CLASS: Record<string, string> = {
  verified: "bg-accent-golden/15 text-accent-golden border-accent-golden/30",
  unverified: SEMANTIC.neutral,
  protected: "bg-accent-blue/15 text-accent-blue border-accent-blue/30",
};

const USER_ROLE_CLASS: Record<string, string> = {
  superuser: "bg-accent-violet/15 text-accent-violet border-accent-violet/30",
  custom: "bg-surface-dark text-surface-mid border-surface-border",
};

const AUDIT_CATEGORY_CLASS: Record<string, string> = {
  security: SEMANTIC.success,
  domain: SEMANTIC.info,
};

const LOG_LEVEL_CLASS: Record<string, string> = {
  error: SEMANTIC.security,
  warning: SEMANTIC.amber,
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
