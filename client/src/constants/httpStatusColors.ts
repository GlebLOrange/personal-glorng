import {
  CONTROL_SIZE,
  CONTROL_SIZE_ICON,
  CONTROL_SIZE_ICON_FIELD,
} from "@/constants/formClasses";

/** HTTP status family keys used for badges and action pills. */
export type HttpStatusFamily = "1xx" | "2xx" | "3xx" | "4xx" | "5xx";

const FAMILY_BADGE: Record<HttpStatusFamily, string> = {
  "1xx": "text-accent-blue bg-accent-blue/15 border-accent-blue/30",
  "2xx": "text-status-success bg-status-success/15 border-status-success/30",
  "3xx": "text-status-warning bg-status-warning/15 border-status-warning/30",
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
    "border-transparent bg-status-warning/3 text-status-warning hover:enabled:bg-status-warning/15 hover:enabled:border-status-warning/40",
  "4xx":
    "border-transparent bg-status-error/3 text-status-error hover:enabled:bg-status-error/15 hover:enabled:border-status-error/40",
  "5xx":
    "border-transparent bg-status-critical/3 text-status-critical hover:enabled:bg-status-critical/15 hover:enabled:border-status-critical/40",
};

const FAMILY_ACTION_SELECTED: Record<HttpStatusFamily, string> = {
  "1xx": "bg-accent-blue/15 border-accent-blue/40 text-accent-blue",
  "2xx": "bg-status-success/15 border-status-success/40 text-status-success",
  "3xx": "bg-status-warning/15 border-status-warning/40 text-status-warning",
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
  `inline-flex ${CONTROL_SIZE} shrink-0 items-center justify-center gap-1.5 whitespace-nowrap rounded-lg border px-4 text-sm font-medium leading-none transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:opacity-50`;

/** Square icon chrome matching CONTROL_SIZE (overrides pill padding). */
export const ICON_ACTION_SIZE = CONTROL_SIZE_ICON;

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
  /** field = in-shell clear (same square as CONTROL_SIZE); default matches CONTROL_SIZE. */
  size?: "md" | "field";
};

/**
 * Classes for square icon chrome (back, pagination, edit, clear).
 * Same idle/hover/selected paint as pills; size forced to square.
 */
export function iconActionClass(
  family: HttpStatusFamily = "1xx",
  selected = false,
  opts: IconActionClassOptions = {},
): string {
  const resolved: HttpStatusFamily = opts.danger ? "4xx" : family;
  const sizeCls = opts.size === "field" ? CONTROL_SIZE_ICON_FIELD : ICON_ACTION_SIZE;
  if (opts.quiet && !selected) {
    const hover = opts.anchor ? "hover:" : "hover:enabled:";
    return [
      sizeCls,
      "border-transparent bg-transparent text-surface-light/60",
      `${hover}border-accent-blue/40 ${hover}bg-accent-blue/15 ${hover}text-accent-blue`,
    ].join(" ");
  }
  if (selected) {
    return `${sizeCls} ${FAMILY_ACTION_SELECTED[resolved]}`;
  }
  const tone = FAMILY_ACTION[resolved];
  if (opts.anchor) {
    return `${sizeCls} ${tone.replaceAll("hover:enabled:", "hover:")}`;
  }
  return `${sizeCls} ${tone}`;
}
