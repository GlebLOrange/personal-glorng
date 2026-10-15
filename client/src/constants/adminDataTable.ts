/** Shared chrome for admin list tables (matches expenses activity). */

export const ADMIN_TABLE_WRAP_CLASS =
  "hidden min-w-0 overflow-x-auto rounded-lg border border-surface-border md:block";

export const ADMIN_TABLE_CLASS = "w-full min-w-0 font-data text-sm";

export const ADMIN_THEAD_ROW_CLASS =
  "border-b border-surface-border bg-surface-card text-left text-surface-mid";

export const ADMIN_TH_CLASS = "px-3 py-1.5 text-xs tracking-wider";

export const ADMIN_TR_CLASS =
  "border-b border-surface-border/60 text-surface-light hover:bg-surface-card/50";

export const ADMIN_TD_CLASS = "px-3 py-1.5 align-middle";

export const ADMIN_TD_MUTED_CLASS = `${ADMIN_TD_CLASS} whitespace-nowrap text-xs text-surface-mid`;

export const ADMIN_TD_TITLE_CLASS = `${ADMIN_TD_CLASS} max-w-[16rem] font-sans`;

export const ADMIN_TD_ACTIONS_CLASS =
  "whitespace-nowrap px-2 py-1.5 align-middle text-right";

export const ADMIN_ACTIONS_CLASS = "inline-flex items-center justify-end gap-0.5";

/** Mobile list: hairline separators under each row. */
export const ADMIN_MOBILE_LIST_CLASS = "flex flex-col md:hidden";

export const ADMIN_MOBILE_ROW_WRAP_CLASS =
  "border-b border-surface-border/60 py-2 last:border-b-0";
