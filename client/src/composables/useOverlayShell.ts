import { nextTick, onUnmounted, watch, type Ref, type WatchSource } from "vue";

import { useScrollLock } from "@/composables/useScrollLock";
import { focusEditableField } from "@/utils/focusField";

/** Focusable controls inside an overlay panel (modal / drawer). */
const FOCUSABLE_SELECTOR = [
  "a[href]",
  "area[href]",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "button:not([disabled])",
  "iframe",
  "object",
  "embed",
  '[tabindex]:not([tabindex="-1"])',
  "[contenteditable]",
].join(", ");

/**
 * Return tabbable elements inside `root` for focus trapping.
 */
export function getOverlayFocusableElements(root: HTMLElement): HTMLElement[] {
  return Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(
    (el) => el.tabIndex >= 0,
  );
}

export type OverlayShellOptions = {
  open: WatchSource<boolean>;
  panelRef: Ref<HTMLElement | null>;
  onClose: () => void;
  /** Fallback when no editable field exists (e.g. close button). */
  initialFocusFallback?: Ref<HTMLElement | null> | (() => HTMLElement | null);
};

/**
 * Shared overlay behavior: scroll lock, Escape, Tab trap, return-focus, initial focus.
 */
export function useOverlayShell(options: OverlayShellOptions): void {
  let returnFocusTarget: HTMLElement | null = null;
  let focusRafId = 0;

  useScrollLock(options.open);

  function resolveFallback(): HTMLElement | null {
    const fallback = options.initialFocusFallback;
    if (!fallback) return null;
    return typeof fallback === "function" ? fallback() : fallback.value;
  }

  function trapFocus(event: KeyboardEvent): void {
    const root = options.panelRef.value;
    if (!root) return;

    const focusables = getOverlayFocusableElements(root);
    if (focusables.length === 0) {
      event.preventDefault();
      return;
    }

    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const active = document.activeElement;

    if (event.shiftKey) {
      if (active === first || !root.contains(active)) {
        last.focus();
        event.preventDefault();
      }
      return;
    }

    if (active === last || !root.contains(active)) {
      first.focus();
      event.preventDefault();
    }
  }

  function onKeydown(event: KeyboardEvent): void {
    if (event.key === "Escape") {
      options.onClose();
      return;
    }
    if (event.key === "Tab") trapFocus(event);
  }

  watch(
    options.open,
    async (open) => {
      cancelAnimationFrame(focusRafId);

      if (!open) {
        document.removeEventListener("keydown", onKeydown);
        await nextTick();
        returnFocusTarget?.focus();
        return;
      }

      returnFocusTarget =
        document.activeElement instanceof HTMLElement ? document.activeElement : null;
      document.addEventListener("keydown", onKeydown);
      await nextTick();

      focusRafId = requestAnimationFrame(() => {
        focusEditableField(options.panelRef.value, resolveFallback() ?? options.panelRef.value);
      });
    },
    { immediate: true },
  );

  onUnmounted(() => {
    cancelAnimationFrame(focusRafId);
    document.removeEventListener("keydown", onKeydown);
  });
}
