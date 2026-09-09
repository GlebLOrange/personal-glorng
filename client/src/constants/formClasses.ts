/** Shared form control classes — 8px grid: default h-10 (40px), compact h-9 (36px). */

/** Default interactive control height — inputs, buttons, icon actions (40px). */
export const CONTROL_SIZE = "box-border h-10";

/** Square side matching CONTROL_SIZE (for icon buttons / clear slots). */
export const CONTROL_SIZE_SQUARE = "w-10 min-w-10";

/** Labeled button sizes — height from CONTROL_SIZE except lg. */
export const CONTROL_BUTTON_MD = `${CONTROL_SIZE} px-4 text-sm`;
export const CONTROL_BUTTON_SM = `${CONTROL_SIZE} px-3 text-xs`;
export const CONTROL_BUTTON_LG = "box-border h-12 px-6 text-base";
export const CONTROL_BUTTON_ICON = `${CONTROL_SIZE} ${CONTROL_SIZE_SQUARE} px-0 text-sm`;

/** Shared chrome for square icon actions (size applied separately). */
const CONTROL_SIZE_ICON_CHROME =
  "inline-flex shrink-0 items-center justify-center box-border rounded-lg border !px-0 text-sm font-medium leading-none transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:opacity-50";

/** Square icon control matching CONTROL_SIZE (40×40 touch target). */
export const CONTROL_SIZE_ICON = `${CONTROL_SIZE_ICON_CHROME} ${CONTROL_SIZE} ${CONTROL_SIZE_SQUARE}`;

/**
 * In-field clear — fill the shell (not another h-10 outside the border box).
 * (ponytail: ceiling is nested bordered icons; upgrade to size token if shells gain padding.)
 */
export const CONTROL_SIZE_ICON_FIELD = `${CONTROL_SIZE_ICON_CHROME} !h-full !w-10 !min-h-0 !min-w-10`;

/** Reserved clear-slot inside field shells (matches shell content box). */
export const FIELD_CLEAR_SLOT = `flex h-full ${CONTROL_SIZE_SQUARE} shrink-0 items-center justify-center`;
export const FIELD_CLEAR_HIDDEN_CLASS = "invisible pointer-events-none";

const FIELD_FOCUS =
  "focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 focus-visible:border-accent-blue";

export const FIELD_WRAPPER_CLASS = "relative min-w-0";
/** Field name on notch / inside / trailing — quieter than body text. */
export const FIELD_LABEL_TEXT_CLASS = "text-label leading-4 text-surface-muted";
export const FIELD_NOTCH_BG_CLASS = "bg-surface-card";
export const FIELD_NOTCH_ROW_CLASS =
  "absolute left-3 top-2.5 z-20 flex max-w-[calc(100%-1.5rem)] -translate-y-[calc(100%-3px)] items-center gap-1 px-1.5";
/**
 * In-control trailing label (same row as the value), left of the select chevron.
 * Chevron sits at right 0.75rem; keep this at right-8 so the caret stays clear.
 */
export const FIELD_INLINE_END_LABEL_CLASS =
  "absolute right-8 top-1/2 z-20 flex max-w-[min(50%,11rem)] -translate-y-1/2 items-center gap-1 bg-transparent";
/** Extra end padding on native selects when an inline end label is present. */
export const SELECT_INLINE_END_PAD_CLASS = "!pr-36";
export const SELECT_INLINE_END_PAD_COMPACT_CLASS = "!pr-32";
export const FIELD_NOTCH_CLASS =
  "pointer-events-none absolute left-3 top-2.5 z-20 max-w-[calc(100%-1.5rem)] -translate-y-[calc(100%-3px)] truncate px-1.5 text-xs leading-4";

export const FIELD_INPUT_CLASS =
  `${CONTROL_SIZE} w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-0 text-surface-light text-sm ` +
  `${FIELD_FOCUS} transition-colors placeholder:text-surface-mid/70`;

export const FIELD_INPUT_CLASS_COMPACT =
  "box-border h-9 bg-surface-dark border border-surface-border rounded-lg px-3 py-0 text-surface-light text-sm " +
  `${FIELD_FOCUS} transition-colors placeholder:text-surface-mid/70`;

export const SELECT_CLASS =
  `field-select-chevron ${CONTROL_SIZE} w-full rounded-lg pl-4 pr-10 py-0 text-surface-light text-sm ` +
  `ring-1 ring-inset ring-surface-border focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 transition-colors`;

export const SELECT_CLASS_COMPACT =
  "field-select-chevron box-border h-9 rounded-lg pl-2 pr-8 py-0 text-surface-light text-xs " +
  "ring-1 ring-inset ring-surface-border focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 transition-colors min-w-[7.5rem]";

export const TEXTAREA_CLASS =
  "min-h-10 w-full bg-surface-card border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm " +
  `${FIELD_FOCUS} transition-colors placeholder:text-surface-mid/70 resize-y disabled:opacity-60`;

export const TEXTAREA_CLASS_COMPACT =
  "min-h-9 w-full bg-surface-card border border-surface-border rounded-lg px-3 py-1.5 text-surface-light text-sm " +
  `${FIELD_FOCUS} transition-colors placeholder:text-surface-mid/70 resize-y disabled:opacity-60`;
