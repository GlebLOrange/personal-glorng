/**
 * Shared width for filters / options toolbar popovers.
 * Prefer width on the panel (`TOOLBAR_POPOVER_PANEL_CLASS`) so the trigger stays content-fit.
 * Chip filter menus teleport a content-fit fixed panel (see AdminFilterDropdown).
 */

/** Options / form popovers: usable min for selects and inputs. */
export const TOOLBAR_POPOVER_WIDTH_CLASS =
  "w-[min(100vw-2rem,28rem)] min-w-[16rem] max-w-full";

/** Panel surface chrome only (use with w-full under a sized root). */
export const TOOLBAR_POPOVER_PANEL_CHROME_CLASS =
  "rounded-lg border border-surface-border bg-surface-card p-3 shadow-lg";

/** Standalone panel: width + chrome (inline cards / non-rooted panels). */
export const TOOLBAR_POPOVER_PANEL_CLASS = [
  TOOLBAR_POPOVER_WIDTH_CLASS,
  TOOLBAR_POPOVER_PANEL_CHROME_CLASS,
].join(" ");
