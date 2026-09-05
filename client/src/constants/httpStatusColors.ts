import { CONTROL_SIZE, CONTROL_SIZE_ICON, CONTROL_SIZE_ICON_FIELD } from "@/constants/formClasses";

/** HTTP status family keys used for badges and action pills. */
export type HttpStatusFamily = "1xx" | "2xx" | "3xx" | "4xx" | "5xx";

type FamilyTone = {
  text: string;
  wash: string;
  tint: string;
  border: string;
  hoverEnabledTint: string;
  hoverEnabledBorder: string;
  hoverEnabledText: string;
  hoverTint: string;
  hoverBorder: string;
  hoverText: string;
  activeEnabledTint: string;
  focusBorder: string;
  focusTint: string;
  focusText: string;
};

const FAMILY_BADGE: Record<HttpStatusFamily, string> = {
  "1xx": "text-accent-blue bg-accent-blue/15 border-accent-blue/30",
  "2xx": "text-status-success bg-status-success/15 border-status-success/30",
  "3xx": "text-status-warning bg-status-warning/15 border-status-warning/30",
  "4xx": "text-status-error bg-status-error/15 border-status-error/30",
  "5xx": "text-status-critical bg-status-critical/15 border-status-critical/30",
};

const FAMILY_TONE: Record<HttpStatusFamily, FamilyTone> = {
  "1xx": {
    text: "text-accent-blue",
    wash: "bg-accent-blue/3",
    tint: "bg-accent-blue/15",
    border: "border-accent-blue/40",
    hoverEnabledTint: "hover:enabled:bg-accent-blue/15",
    hoverEnabledBorder: "hover:enabled:border-accent-blue/40",
    hoverEnabledText: "hover:enabled:text-accent-blue",
    hoverTint: "hover:bg-accent-blue/15",
    hoverBorder: "hover:border-accent-blue/40",
    hoverText: "hover:text-accent-blue",
    activeEnabledTint: "active:enabled:bg-accent-blue/25",
    focusBorder: "focus-visible:border-accent-blue/40",
    focusTint: "focus-visible:bg-accent-blue/15",
    focusText: "focus-visible:text-accent-blue",
  },
  "2xx": {
    text: "text-status-success",
    wash: "bg-status-success/3",
    tint: "bg-status-success/15",
    border: "border-status-success/40",
    hoverEnabledTint: "hover:enabled:bg-status-success/15",
    hoverEnabledBorder: "hover:enabled:border-status-success/40",
    hoverEnabledText: "hover:enabled:text-status-success",
    hoverTint: "hover:bg-status-success/15",
    hoverBorder: "hover:border-status-success/40",
    hoverText: "hover:text-status-success",
    activeEnabledTint: "active:enabled:bg-status-success/25",
    focusBorder: "focus-visible:border-status-success/40",
    focusTint: "focus-visible:bg-status-success/15",
    focusText: "focus-visible:text-status-success",
  },
  "3xx": {
    text: "text-status-warning",
    wash: "bg-status-warning/3",
    tint: "bg-status-warning/15",
    border: "border-status-warning/40",
    hoverEnabledTint: "hover:enabled:bg-status-warning/15",
    hoverEnabledBorder: "hover:enabled:border-status-warning/40",
    hoverEnabledText: "hover:enabled:text-status-warning",
    hoverTint: "hover:bg-status-warning/15",
    hoverBorder: "hover:border-status-warning/40",
    hoverText: "hover:text-status-warning",
    activeEnabledTint: "active:enabled:bg-status-warning/25",
    focusBorder: "focus-visible:border-status-warning/40",
    focusTint: "focus-visible:bg-status-warning/15",
    focusText: "focus-visible:text-status-warning",
  },
  "4xx": {
    text: "text-status-error",
    wash: "bg-status-error/3",
    tint: "bg-status-error/15",
    border: "border-status-error/40",
    hoverEnabledTint: "hover:enabled:bg-status-error/15",
    hoverEnabledBorder: "hover:enabled:border-status-error/40",
    hoverEnabledText: "hover:enabled:text-status-error",
    hoverTint: "hover:bg-status-error/15",
    hoverBorder: "hover:border-status-error/40",
    hoverText: "hover:text-status-error",
    activeEnabledTint: "active:enabled:bg-status-error/25",
    focusBorder: "focus-visible:border-status-error/40",
    focusTint: "focus-visible:bg-status-error/15",
    focusText: "focus-visible:text-status-error",
  },
  "5xx": {
    text: "text-status-critical",
    wash: "bg-status-critical/3",
    tint: "bg-status-critical/15",
    border: "border-status-critical/40",
    hoverEnabledTint: "hover:enabled:bg-status-critical/15",
    hoverEnabledBorder: "hover:enabled:border-status-critical/40",
    hoverEnabledText: "hover:enabled:text-status-critical",
    hoverTint: "hover:bg-status-critical/15",
    hoverBorder: "hover:border-status-critical/40",
    hoverText: "hover:text-status-critical",
    activeEnabledTint: "active:enabled:bg-status-critical/25",
    focusBorder: "focus-visible:border-status-critical/40",
    focusTint: "focus-visible:bg-status-critical/15",
    focusText: "focus-visible:text-status-critical",
  },
};

type FamilyToneClassOptions = {
  quiet?: boolean;
  anchor?: boolean;
  includeActive?: boolean;
  includeFocusTint?: boolean;
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

/**
 * Shared family paint used by pills, icon actions, and lightweight buttons.
 * ponytail: static class pieces keep Tailwind detection intact; grow the map only when a new state family is truly needed.
 */
export function familyToneClass(
  family: HttpStatusFamily,
  selected = false,
  options: FamilyToneClassOptions = {},
): string {
  const tone = FAMILY_TONE[family];

  if (selected) {
    return [tone.tint, tone.border, tone.text].join(" ");
  }

  if (options.quiet) {
    return [
      "border-transparent bg-transparent text-surface-light/60",
      options.anchor ? tone.hoverBorder : tone.hoverEnabledBorder,
      options.anchor ? tone.hoverTint : tone.hoverEnabledTint,
      options.anchor ? tone.hoverText : tone.hoverEnabledText,
      options.includeFocusTint ? [tone.focusBorder, tone.focusTint, tone.focusText].join(" ") : "",
    ]
      .filter(Boolean)
      .join(" ");
  }

  return [
    "border-transparent",
    tone.wash,
    tone.text,
    options.anchor ? tone.hoverBorder : tone.hoverEnabledBorder,
    options.anchor ? tone.hoverTint : tone.hoverEnabledTint,
    options.includeActive ? tone.activeEnabledTint : "",
  ]
    .filter(Boolean)
    .join(" ");
}

/** Shared shape for toolbar/tab action pills. */
export const ACTION_PILL_BASE = `inline-flex ${CONTROL_SIZE} shrink-0 items-center justify-center gap-1.5 whitespace-nowrap rounded-lg border px-4 text-sm font-medium leading-none transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:opacity-50`;

/** Square icon chrome matching CONTROL_SIZE (overrides pill padding). */
export const ICON_ACTION_SIZE = CONTROL_SIZE_ICON;

/**
 * Classes for an action pill in a given HTTP-family color.
 * Idle = /3 wash + family text, no border; hover/selected = /15 + /40 border.
 */
export function actionFamilyClass(family: HttpStatusFamily, selected = false): string {
  return `${ACTION_PILL_BASE} ${familyToneClass(family, selected)}`;
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
  return `${sizeCls} ${familyToneClass(resolved, selected, {
    quiet: opts.quiet,
    anchor: opts.anchor,
  })}`;
}
