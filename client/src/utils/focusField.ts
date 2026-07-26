import { nextTick } from "vue";

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

/**
 * Focus an element after the next paint (e.g. newly rendered `role="alert"`).
 * Target should be focusable (`tabindex="-1"` for non-interactive alerts).
 * Pass a getter when the element mounts on the same tick as the call.
 */
export async function focusAfterPaint(
  el: HTMLElement | null | undefined | (() => HTMLElement | null | undefined),
): Promise<void> {
  await nextTick();
  const target = typeof el === "function" ? el() : el;
  target?.focus();
}
