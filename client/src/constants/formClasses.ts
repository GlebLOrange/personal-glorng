/** Shared form control classes — 8px grid: default min-h-11 (44px), compact min-h-9 (36px). */

const FIELD_FOCUS =
  "focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 focus-visible:border-accent-blue";

export const FIELD_INPUT_CLASS =
  "h-11 w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-0 text-surface-light text-sm " +
  `${FIELD_FOCUS} transition-colors placeholder:text-surface-mid/70`;

export const FIELD_INPUT_CLASS_COMPACT =
  "h-9 bg-surface-dark border border-surface-border rounded-lg px-3 py-0 text-surface-light text-sm " +
  `${FIELD_FOCUS} transition-colors placeholder:text-surface-mid/70`;

export const SELECT_CLASS =
  "h-11 bg-surface-dark border border-surface-border rounded-lg px-4 py-0 text-surface-light text-sm " +
  `${FIELD_FOCUS} transition-colors`;

export const SELECT_CLASS_COMPACT =
  "h-9 bg-surface-dark border border-surface-border rounded-lg px-2 py-0 text-surface-light text-xs " +
  `${FIELD_FOCUS} transition-colors min-w-[7.5rem]`;

export const TEXTAREA_CLASS =
  "min-h-11 w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm " +
  `${FIELD_FOCUS} transition-colors placeholder:text-surface-mid/70 resize-y disabled:opacity-60`;
