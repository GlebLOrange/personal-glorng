/**
 * Shared chrome / width for filters / options toolbar popovers.
 * Fixed mid column on trigger + panel — same width open or closed (no jump).
 */

/** Mid column (~16rem); caps on narrow viewports. */
export const TOOLBAR_POPOVER_WIDTH_CLASS =
  "w-64 max-w-[min(100vw-2rem,28rem)]";

/** Panel surface chrome only. */
export const TOOLBAR_POPOVER_PANEL_CHROME_CLASS =
  "rounded-lg border border-surface-border bg-surface-card p-3 shadow-lg";

/** Standalone panel: mid width + chrome. */
export const TOOLBAR_POPOVER_PANEL_CLASS = [
  TOOLBAR_POPOVER_WIDTH_CLASS,
  TOOLBAR_POPOVER_PANEL_CHROME_CLASS,
].join(" ");
