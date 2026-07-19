/** Prefer a typing field over chrome controls (e.g. modal Close). */
const EDITABLE_FIELD_SELECTOR = [
  'input:not([disabled]):not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="button"]):not([type="submit"]):not([type="reset"])',
  "select:not([disabled])",
  "textarea:not([disabled])",
].join(", ");

/**
 * First editable field in `root` (text-like input, select, or textarea).
 */
export function queryEditableField(root: ParentNode): HTMLElement | null {
  return root.querySelector<HTMLElement>(EDITABLE_FIELD_SELECTOR);
}

/**
 * Focus the first editable field in `root`, or `fallback` when none exists.
 */
export function focusEditableField(
  root: ParentNode | null | undefined,
  fallback?: HTMLElement | null,
): void {
  const target = (root && queryEditableField(root)) || fallback || null;
  target?.focus();
}
