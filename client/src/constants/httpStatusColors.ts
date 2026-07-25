/** HTTP status family keys used for badges and action pills. */
export type HttpStatusFamily = "1xx" | "2xx" | "3xx" | "4xx" | "5xx";

const FAMILY_BADGE: Record<HttpStatusFamily, string> = {
  "1xx": "text-accent-blue bg-accent-blue/15 border-accent-blue/30",
  "2xx": "text-status-success bg-status-success/15 border-status-success/30",
  "3xx": "text-status-yellow bg-status-yellow/15 border-status-yellow/30",
  "4xx": "text-status-error bg-status-error/15 border-status-error/30",
  "5xx": "text-status-critical bg-status-critical/15 border-status-critical/30",
};

/** Option C: idle = /3 wash + family text, no border; hover/selected = /15 + /40 border. */
const FAMILY_ACTION: Record<HttpStatusFamily, string> = {
  "1xx":
    "border-transparent bg-accent-blue/3 text-accent-blue hover:enabled:bg-accent-blue/15 hover:enabled:border-accent-blue/40",
  "2xx":
    "border-transparent bg-status-success/3 text-status-success hover:enabled:bg-status-success/15 hover:enabled:border-status-success/40",
  "3xx":
    "border-transparent bg-status-yellow/3 text-status-yellow hover:enabled:bg-status-yellow/15 hover:enabled:border-status-yellow/40",
  "4xx":
    "border-transparent bg-status-error/3 text-status-error hover:enabled:bg-status-error/15 hover:enabled:border-status-error/40",
  "5xx":
    "border-transparent bg-status-critical/3 text-status-critical hover:enabled:bg-status-critical/15 hover:enabled:border-status-critical/40",
};

const FAMILY_ACTION_SELECTED: Record<HttpStatusFamily, string> = {
  "1xx": "bg-accent-blue/15 border-accent-blue/40 text-accent-blue",
  "2xx": "bg-status-success/15 border-status-success/40 text-status-success",
  "3xx": "bg-status-yellow/15 border-status-yellow/40 text-status-yellow",
  "4xx": "bg-status-error/15 border-status-error/40 text-status-error",
  "5xx": "bg-status-critical/15 border-status-critical/40 text-status-critical",
};

/** Map an HTTP status code to its 1xx–5xx family. */
export function httpStatusFamily(code: number): HttpStatusFamily {
  if (code >= 500) return "5xx";
  if (code >= 400) return "4xx";
  if (code >= 300) return "3xx";
  if (code >= 200) return "2xx";
  if (code >= 100) return "1xx";
  return "5xx";
}

/** Pale badge classes for an HTTP status family (shared by StatusBadge / filter chips). */
export function familyBadgeClass(family: HttpStatusFamily): string {
  return FAMILY_BADGE[family];
}

/** Pale badge classes for an HTTP status code. */
export function httpStatusClass(code: number): string {
  return familyBadgeClass(httpStatusFamily(code));
}

/** Shared shape for toolbar/tab action pills. */
export const ACTION_PILL_BASE =
  "inline-flex h-11 shrink-0 items-center justify-center gap-1.5 whitespace-nowrap rounded-lg border px-4 text-sm font-medium leading-none transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:opacity-50";

/** h-8 square chrome — overrides ACTION_PILL_BASE height/padding. */
export const ICON_ACTION_SIZE =
  "inline-flex !h-8 !w-8 !min-h-8 !min-w-8 shrink-0 items-center justify-center rounded-lg border !px-0 text-sm font-medium leading-none transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:opacity-50";

/**
 * Classes for an action pill in a given HTTP-family color.
 * Idle = /3 wash + family text, no border; hover/selected = /15 + /40 border.
 */
export function actionFamilyClass(family: HttpStatusFamily, selected = false): string {
  if (selected) {
    return `${ACTION_PILL_BASE} ${FAMILY_ACTION_SELECTED[family]}`;
  }
  return `${ACTION_PILL_BASE} ${FAMILY_ACTION[family]}`;
}

export type IconActionClassOptions = {
  quiet?: boolean;
  danger?: boolean;
  /** Anchors ignore :enabled — use plain hover: */
  anchor?: boolean;
};

/**
 * Classes for h-8 icon chrome (back, pagination, edit, clear).
 * Same idle/hover/selected paint as pills; size forced to square.
 */
export function iconActionClass(
  family: HttpStatusFamily = "1xx",
  selected = false,
  opts: IconActionClassOptions = {},
): string {
  const resolved: HttpStatusFamily = opts.danger ? "4xx" : family;
  if (opts.quiet && !selected) {
    const hover = opts.anchor ? "hover:" : "hover:enabled:";
    return [
      ICON_ACTION_SIZE,
      "border-transparent bg-transparent text-surface-light/60",
      `${hover}border-accent-blue/40 ${hover}bg-accent-blue/15 ${hover}text-accent-blue`,
    ].join(" ");
  }
  if (selected) {
    return `${ICON_ACTION_SIZE} ${FAMILY_ACTION_SELECTED[resolved]}`;
  }
  const tone = FAMILY_ACTION[resolved];
  if (opts.anchor) {
    return `${ICON_ACTION_SIZE} ${tone.replaceAll("hover:enabled:", "hover:")}`;
  }
  return `${ICON_ACTION_SIZE} ${tone}`;
}
