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

/**
 * Pale product button washes — label ink at 88%, fills lighter than badges.
 * ponytail: static strings only so Tailwind keeps generating utilities.
 */
export const ACTION_BUTTON_PAINT = {
  idleFill: 10,
  hoverFill: 12,
  activeFill: 14,
  selectedFill: 12,
  border: 22,
  labelText: 88,
} as const;

const FAMILY_TONE: Record<HttpStatusFamily, FamilyTone> = {
  "1xx": {
    text: "text-accent-blue/88",
    wash: "bg-accent-blue/10",
    tint: "bg-accent-blue/12",
    border: "border-accent-blue/22",
    hoverEnabledTint: "hover:enabled:bg-accent-blue/12",
    hoverEnabledBorder: "hover:enabled:border-accent-blue/22",
    hoverEnabledText: "hover:enabled:text-accent-blue/88",
    hoverTint: "hover:bg-accent-blue/12",
    hoverBorder: "hover:border-accent-blue/22",
    hoverText: "hover:text-accent-blue/88",
    activeEnabledTint: "active:enabled:bg-accent-blue/14",
    focusBorder: "focus-visible:border-accent-blue/22",
    focusTint: "focus-visible:bg-accent-blue/12",
    focusText: "focus-visible:text-accent-blue/88",
  },
  "2xx": {
    text: "text-status-success/88",
    wash: "bg-status-success/10",
    tint: "bg-status-success/12",
    border: "border-status-success/22",
    hoverEnabledTint: "hover:enabled:bg-status-success/12",
    hoverEnabledBorder: "hover:enabled:border-status-success/22",
    hoverEnabledText: "hover:enabled:text-status-success/88",
    hoverTint: "hover:bg-status-success/12",
    hoverBorder: "hover:border-status-success/22",
    hoverText: "hover:text-status-success/88",
    activeEnabledTint: "active:enabled:bg-status-success/14",
    focusBorder: "focus-visible:border-status-success/22",
    focusTint: "focus-visible:bg-status-success/12",
    focusText: "focus-visible:text-status-success/88",
  },
  "3xx": {
    text: "text-status-warning/88",
    wash: "bg-status-warning/10",
    tint: "bg-status-warning/12",
    border: "border-status-warning/22",
    hoverEnabledTint: "hover:enabled:bg-status-warning/12",
    hoverEnabledBorder: "hover:enabled:border-status-warning/22",
    hoverEnabledText: "hover:enabled:text-status-warning/88",
    hoverTint: "hover:bg-status-warning/12",
    hoverBorder: "hover:border-status-warning/22",
    hoverText: "hover:text-status-warning/88",
    activeEnabledTint: "active:enabled:bg-status-warning/14",
    focusBorder: "focus-visible:border-status-warning/22",
    focusTint: "focus-visible:bg-status-warning/12",
    focusText: "focus-visible:text-status-warning/88",
  },
  "4xx": {
    text: "text-status-error/88",
    wash: "bg-status-error/10",
    tint: "bg-status-error/12",
    border: "border-status-error/22",
    hoverEnabledTint: "hover:enabled:bg-status-error/12",
    hoverEnabledBorder: "hover:enabled:border-status-error/22",
    hoverEnabledText: "hover:enabled:text-status-error/88",
    hoverTint: "hover:bg-status-error/12",
    hoverBorder: "hover:border-status-error/22",
    hoverText: "hover:text-status-error/88",
    activeEnabledTint: "active:enabled:bg-status-error/14",
    focusBorder: "focus-visible:border-status-error/22",
    focusTint: "focus-visible:bg-status-error/12",
    focusText: "focus-visible:text-status-error/88",
  },
  "5xx": {
    text: "text-status-critical/88",
    wash: "bg-status-critical/10",
    tint: "bg-status-critical/12",
    border: "border-status-critical/22",
    hoverEnabledTint: "hover:enabled:bg-status-critical/12",
    hoverEnabledBorder: "hover:enabled:border-status-critical/22",
    hoverEnabledText: "hover:enabled:text-status-critical/88",
    hoverTint: "hover:bg-status-critical/12",
    hoverBorder: "hover:border-status-critical/22",
    hoverText: "hover:text-status-critical/88",
    activeEnabledTint: "active:enabled:bg-status-critical/14",
    focusBorder: "focus-visible:border-status-critical/22",
    focusTint: "focus-visible:bg-status-critical/12",
    focusText: "focus-visible:text-status-critical/88",
  },
};

type FamilyToneClassOptions = {
  quiet?: boolean;
  anchor?: boolean;
  includeActive?: boolean;
  includeFocusTint?: boolean;
  /** Idle bg transparent; hover/focus add family wash (icon clear/edit/remove/copy). */
  transparentIdle?: boolean;
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

  const hoverBorder = options.anchor ? tone.hoverBorder : tone.hoverEnabledBorder;
  const hoverTint = options.anchor ? tone.hoverTint : tone.hoverEnabledTint;
  const hoverText = options.anchor ? tone.hoverText : tone.hoverEnabledText;
  const focusClasses =
    options.includeFocusTint || options.transparentIdle
      ? [tone.focusBorder, tone.focusTint, tone.focusText].join(" ")
      : "";

  if (options.quiet) {
    return [
      "border-transparent bg-transparent text-surface-light/60",
      hoverBorder,
      hoverTint,
      hoverText,
      focusClasses,
    ]
      .filter(Boolean)
      .join(" ");
  }

  if (options.transparentIdle) {
    return [
      "border-transparent bg-transparent",
      tone.text,
      hoverBorder,
      hoverTint,
      options.includeActive ? tone.activeEnabledTint : "",
      focusClasses,
    ]
      .filter(Boolean)
      .join(" ");
  }

  return [
    "border-transparent",
    tone.wash,
    tone.text,
    hoverBorder,
    hoverTint,
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
 * Idle = /10 wash + /88 label; hover/selected = /12 + /22 border (ACTION_BUTTON_PAINT).
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
  /** Idle bg transparent; hover/focus add family wash (clear/edit/remove/copy). */
  transparentIdle?: boolean;
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
    transparentIdle: opts.transparentIdle,
  })}`;
}
