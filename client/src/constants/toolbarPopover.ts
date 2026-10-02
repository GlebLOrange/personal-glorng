/**
 * Shared chrome / width for filters / options toolbar popovers.
 * Trigger min-width is measured from dropdown content (AdminFilterDropdown);
 * CSS only caps to the viewport.
 */

/** Viewport / layout cap shared by trigger + panel. */
export const TOOLBAR_POPOVER_MAX_WIDTH_CLASS = "max-w-[min(100vw-2rem,28rem)]";

/**
 * Panel: hug content, never narrower than the trigger column.
 * - `min-w-full` covers absolute panels under a trigger-sized parent.
 * - Teleported panels set inline minWidth from the trigger in JS.
 */
export const TOOLBAR_POPOVER_PANEL_WIDTH_CLASS = `w-max min-w-full ${TOOLBAR_POPOVER_MAX_WIDTH_CLASS}`;

/** Panel surface chrome only. */
export const TOOLBAR_POPOVER_PANEL_CHROME_CLASS =
  "rounded-lg border border-surface-border bg-surface-card p-3 shadow-lg";

/**
 * Shared row inside filter/options panels — chips, footer actions, clear.
 * Locked h-9 so icon rows and text rows match (not toolbar h-10).
 */
export const FILTER_MENU_ROW_CLASS =
  "box-border flex h-9 w-full shrink-0 items-center gap-1.5 whitespace-nowrap rounded-lg border px-2 text-left text-xs leading-none transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:cursor-not-allowed disabled:opacity-50";
