/** HTTP status family keys used for badges and action pills. */
export type HttpStatusFamily = "1xx" | "2xx" | "3xx" | "4xx" | "5xx";

const FAMILY_BADGE: Record<HttpStatusFamily, string> = {
  "1xx": "text-accent-blue bg-accent-blue/15 border-accent-blue/30",
  "2xx": "text-status-success bg-status-success/15 border-status-success/30",
  "3xx": "text-status-cyan bg-status-cyan/15 border-status-cyan/30",
  "4xx": "text-status-error bg-status-error/15 border-status-error/30",
  "5xx": "text-status-critical bg-status-critical/15 border-status-critical/30",
};

/** Option C: idle fill/3 + matching accent text. Hover/selected: pale /15 bg + matching border. */
const FAMILY_ACTION: Record<HttpStatusFamily, string> = {
  "1xx":
    "border-transparent bg-accent-blue/3 text-accent-blue hover:enabled:bg-accent-blue/15 hover:enabled:border-accent-blue/40",
  "2xx":
    "border-transparent bg-status-success/3 text-status-success hover:enabled:bg-status-success/15 hover:enabled:border-status-success/40",
  "3xx":
    "border-transparent bg-status-cyan/3 text-status-cyan hover:enabled:bg-status-cyan/15 hover:enabled:border-status-cyan/40",
  "4xx":
    "border-transparent bg-status-error/3 text-status-error hover:enabled:bg-status-error/15 hover:enabled:border-status-error/40",
  "5xx":
    "border-transparent bg-status-critical/3 text-status-critical hover:enabled:bg-status-critical/15 hover:enabled:border-status-critical/40",
};

const FAMILY_ACTION_SELECTED: Record<HttpStatusFamily, string> = {
  "1xx": "bg-accent-blue/15 border-accent-blue/40 text-accent-blue",
  "2xx": "bg-status-success/15 border-status-success/40 text-status-success",
  "3xx": "bg-status-cyan/15 border-status-cyan/40 text-status-cyan",
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

/** Pale badge classes for an HTTP status code. */
export function httpStatusClass(code: number): string {
  return FAMILY_BADGE[httpStatusFamily(code)];
}

/** Shared shape for toolbar/tab action pills. */
export const ACTION_PILL_BASE =
  "inline-flex h-11 shrink-0 items-center justify-center gap-1.5 whitespace-nowrap rounded-lg border px-4 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:opacity-50";

/**
 * Classes for an action pill in a given HTTP-family color.
 * Idle = fill at 3% opacity + matching accent text; hover/selected = pale /15 + border.
 */
export function actionFamilyClass(family: HttpStatusFamily, selected = false): string {
  if (selected) {
    return `${ACTION_PILL_BASE} ${FAMILY_ACTION_SELECTED[family]}`;
  }
  return `${ACTION_PILL_BASE} ${FAMILY_ACTION[family]}`;
}
