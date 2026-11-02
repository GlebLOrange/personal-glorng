import { familyToneClass, type HttpStatusFamily } from "@/constants/httpStatusColors";

/**
 * Semantic product actions mapped to HTTP status color families (1xx–5xx).
 * Use these names on BaseButton `variant` or ToolbarPillButton `action`.
 */
export type SemanticButtonAction =
  "create" | "add" | "save" | "edit" | "remove" | "delete" | "cancel";

/**
 * HTTP family for pills/icons that still paint via familyToneClass.
 * save → primary (1xx). edit → primary wash on icon chrome (transparentIdle).
 * cancel stays 5xx for rare icon use; BaseButton `cancel` uses ghost via classesForActionButton.
 */
export const SEMANTIC_ACTION_HTTP_FAMILY: Record<SemanticButtonAction, HttpStatusFamily> = {
  create: "1xx",
  add: "1xx",
  save: "1xx",
  edit: "1xx",
  remove: "4xx",
  delete: "4xx",
  cancel: "5xx",
};

/** BaseButton variants — semantic actions plus layout/neutral chrome. */
export type BaseButtonVariant =
  "primary" | "secondary" | "ghost" | "success" | SemanticButtonAction;

const FOCUS_RING: Record<HttpStatusFamily, string> = {
  "1xx": "focus-visible:ring-accent-coral/50",
  "2xx": "focus-visible:ring-status-success/50",
  "3xx": "focus-visible:ring-status-warning/50",
  "4xx": "focus-visible:ring-status-error/50",
  "5xx": "focus-visible:ring-status-critical/50",
};

/** Product chrome: primary wash + error wash. Edit/cancel use surface/ghost below. */
const WASHED_VARIANT_FAMILY: Partial<Record<BaseButtonVariant, HttpStatusFamily>> = {
  primary: "1xx",
  create: "1xx",
  add: "1xx",
  success: "1xx",
  save: "1xx",
  remove: "4xx",
  delete: "4xx",
};

const NEUTRAL_FOCUS = "focus-visible:ring-accent-coral/50";

const NEUTRAL_GHOST_IDLE =
  "border-transparent bg-transparent text-surface-light/80 hover:enabled:border-surface-light/40 hover:enabled:bg-surface-light/10 hover:enabled:text-surface-light active:enabled:bg-surface-light/15";

const NEUTRAL_GHOST_QUIET =
  "border-transparent bg-transparent text-surface-light/60 hover:enabled:border-surface-light/40 hover:enabled:bg-surface-light/10 hover:enabled:text-surface-light focus-visible:border-surface-light/40 focus-visible:bg-surface-light/10 focus-visible:text-surface-light";

/** Resting grayscale fill — distinct from transparent ghost. */
const NEUTRAL_SECONDARY_IDLE =
  "border-surface-border bg-surface-card text-surface-light/80 hover:enabled:border-surface-light/40 hover:enabled:bg-surface-light/10 hover:enabled:text-surface-light active:enabled:bg-surface-light/15";

const NEUTRAL_SELECTED = "border-surface-light/40 bg-surface-light/15 text-surface-light";

type ActionButtonClassInput = {
  variant: BaseButtonVariant;
  selected?: boolean;
  quiet?: boolean;
  /** Prefer variant `delete` / `remove`; still forces 4xx when true. */
  danger?: boolean;
};

function washedFamilyClasses(family: HttpStatusFamily, selected: boolean): string {
  return `${familyToneClass(family, selected, { includeActive: true })} ${FOCUS_RING[family]}`;
}

/**
 * Tailwind classes for BaseButton from variant + flags.
 * ponytail: single resolver keeps HTTP-family paint in one place.
 */
export function classesForActionButton(input: ActionButtonClassInput): string {
  const selected = Boolean(input.selected);
  const quiet = Boolean(input.quiet);
  const variant = input.variant;

  if (input.danger) {
    if (variant === "ghost" || quiet) {
      return familyToneClass("4xx", selected, {
        quiet: true,
        includeFocusTint: true,
      });
    }
    return washedFamilyClasses("4xx", selected);
  }

  const family = WASHED_VARIANT_FAMILY[variant];
  if (family) {
    return washedFamilyClasses(family, selected);
  }

  // cancel + ghost — muted until hover (sheet has no 5xx cancel hue)
  if (variant === "ghost" || variant === "cancel") {
    if (quiet && !selected) {
      return NEUTRAL_GHOST_QUIET;
    }
    if (selected) {
      return `${NEUTRAL_SELECTED} ${NEUTRAL_FOCUS}`;
    }
    return `${NEUTRAL_GHOST_IDLE} ${NEUTRAL_FOCUS}`;
  }

  // secondary + edit — surface outline (sheet secondary fill == primary)
  if (selected) {
    return `${NEUTRAL_SELECTED} ${NEUTRAL_FOCUS}`;
  }
  return `${NEUTRAL_SECONDARY_IDLE} ${NEUTRAL_FOCUS}`;
}
