import { familyToneClass, type HttpStatusFamily } from "@/constants/httpStatusColors";

/**
 * Semantic product actions mapped to HTTP status color families (1xx–5xx).
 * Use these names on BaseButton `variant` or ToolbarPillButton `action`.
 */
export type SemanticButtonAction =
  | "create"
  | "add"
  | "save"
  | "edit"
  | "remove"
  | "delete"
  | "cancel";

export const SEMANTIC_ACTION_HTTP_FAMILY: Record<SemanticButtonAction, HttpStatusFamily> = {
  create: "1xx",
  add: "1xx",
  save: "2xx",
  edit: "3xx",
  remove: "4xx",
  delete: "4xx",
  cancel: "5xx",
};

/** BaseButton variants — semantic actions plus layout/neutral chrome. */
export type BaseButtonVariant =
  | "primary"
  | "secondary"
  | "ghost"
  | "success"
  | SemanticButtonAction;

export function httpFamilyForSemanticAction(action: SemanticButtonAction): HttpStatusFamily {
  return SEMANTIC_ACTION_HTTP_FAMILY[action];
}

type WashFamily = "2xx" | "3xx" | "4xx" | "5xx";

const WASH_FOCUS_RING: Record<WashFamily, string> = {
  "2xx": "focus-visible:ring-status-success/50",
  "3xx": "focus-visible:ring-status-warning/50",
  "4xx": "focus-visible:ring-status-error/50",
  "5xx": "focus-visible:ring-status-critical/50",
};

export type ActionButtonClassInput = {
  variant: BaseButtonVariant;
  selected?: boolean;
  quiet?: boolean;
  /** Prefer variant `delete` / `remove`; still forces 4xx when true. */
  danger?: boolean;
};

/**
 * Tailwind classes for BaseButton from variant + flags.
 * ponytail: single resolver keeps HTTP-family paint in one place.
 */
export function classesForActionButton(input: ActionButtonClassInput): string {
  const selected = Boolean(input.selected);
  const quiet = Boolean(input.quiet);

  if (input.danger) {
    if (input.variant === "ghost" || quiet) {
      return familyToneClass("4xx", selected, {
        quiet: true,
        includeFocusTint: true,
      });
    }
    return `${familyToneClass("4xx", selected, { includeActive: true })} ${WASH_FOCUS_RING["4xx"]}`;
  }

  const variant = input.variant === "success" ? "save" : input.variant;

  if (variant === "save") {
    return `${familyToneClass("2xx", selected, { includeActive: true })} ${WASH_FOCUS_RING["2xx"]}`;
  }

  if (variant === "cancel") {
    return `${familyToneClass("5xx", selected, { includeActive: true })} ${WASH_FOCUS_RING["5xx"]}`;
  }

  if (variant === "edit") {
    return `${familyToneClass("3xx", selected, { includeActive: true })} ${WASH_FOCUS_RING["3xx"]}`;
  }

  if (variant === "remove" || variant === "delete") {
    return `${familyToneClass("4xx", selected, { includeActive: true })} ${WASH_FOCUS_RING["4xx"]}`;
  }

  if (variant === "create" || variant === "add" || variant === "primary") {
    return [
      "border-transparent bg-accent-blue text-on-accent",
      "hover:enabled:bg-accent-blue/90 active:enabled:bg-accent-blue/80",
      selected ? "ring-1 ring-inset ring-accent-blue/40" : "",
    ]
      .filter(Boolean)
      .join(" ");
  }

  if (variant === "ghost") {
    if (quiet && !selected) {
      return [
        "border-transparent bg-transparent text-surface-light/60",
        "hover:enabled:border-surface-light/40 hover:enabled:bg-surface-light/10 hover:enabled:text-surface-light",
        "focus-visible:border-surface-light/40 focus-visible:bg-surface-light/10 focus-visible:text-surface-light",
      ].join(" ");
    }
    if (selected) {
      return "border-surface-light/40 bg-surface-light/15 text-surface-light";
    }
    return "border-transparent bg-transparent text-surface-light/80 hover:enabled:border-surface-light/40 hover:enabled:bg-surface-light/10 hover:enabled:text-surface-light active:enabled:bg-surface-light/15";
  }

  // secondary — neutral OAuth / unlink / promote
  if (selected) {
    return "border-surface-light/40 bg-surface-light/15 text-surface-light";
  }
  return "border-transparent bg-transparent text-surface-light/80 hover:enabled:border-surface-light/40 hover:enabled:bg-surface-light/10 hover:enabled:text-surface-light active:enabled:bg-surface-light/15";
}
