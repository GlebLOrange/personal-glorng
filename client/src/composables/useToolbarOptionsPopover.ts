import { nextTick, onMounted, onUnmounted, watch, type Ref } from "vue";

import { getOverlayFocusableElements, trapTabKeyInRoot } from "@/composables/useOverlayShell";

export type ToolbarOptionsPopoverOptions = {
  open: Ref<boolean>;
  rootRef: Ref<HTMLElement | null>;
  panelRef: Ref<HTMLElement | null>;
  /** Optional trigger for focus restore when previouslyFocused is unavailable. */
  triggerRef?: Ref<HTMLElement | { $el?: HTMLElement } | null>;
};

function resolveTriggerEl(
  trigger: HTMLElement | { $el?: HTMLElement } | null | undefined,
): HTMLElement | null {
  if (!trigger) return null;
  if (trigger instanceof HTMLElement) return trigger;
  const el = trigger.$el;
  return el instanceof HTMLElement ? el : null;
}

/**
 * Shared open/close behavior for toolbar options popovers (capture click-outside,
 * Escape, Tab trap, first-focusable on open, focus restore on close).
 */
export function useToolbarOptionsPopover(options: ToolbarOptionsPopoverOptions): {
  close: () => void;
  toggle: () => void;
} {
  const { open, rootRef, panelRef, triggerRef } = options;
  let previouslyFocused: HTMLElement | null = null;

  function close(): void {
    open.value = false;
  }

  function toggle(): void {
    open.value = !open.value;
  }

  function focusTrigger(): void {
    const el = resolveTriggerEl(triggerRef?.value);
    el?.focus();
  }

  function onDocumentClick(event: MouseEvent): void {
    if (!open.value) return;
    const target = event.target as Node;
    const root = rootRef.value;
    const panel = panelRef.value;
    // Panel may be Teleported outside root (e.g. AdminFilterDropdown).
    if (root?.contains(target) || panel?.contains(target)) return;
    close();
  }

  function onKeydown(event: KeyboardEvent): void {
    if (!open.value) return;

    if (event.key === "Escape") {
      event.stopPropagation();
      event.preventDefault();
      close();
      return;
    }

    trapTabKeyInRoot(event, panelRef.value);
  }

  watch(open, async (isOpen) => {
    if (isOpen) {
      previouslyFocused = document.activeElement as HTMLElement | null;
      await nextTick();
      const panel = panelRef.value;
      if (!panel) return;
      const focusables = getOverlayFocusableElements(panel);
      const preferred =
        focusables.find(
          (el) =>
            el instanceof HTMLInputElement ||
            el instanceof HTMLSelectElement ||
            el instanceof HTMLTextAreaElement,
        ) ?? focusables[0];
      if (preferred) {
        preferred.focus();
      } else {
        panel.focus();
      }
      return;
    }
    const restore = previouslyFocused;
    previouslyFocused = null;
    if (restore) {
      restore.focus();
    } else {
      focusTrigger();
    }
  });

  onMounted(() => {
    // Capture: drawer panels use @click.stop, which blocks bubble-phase document listeners.
    document.addEventListener("click", onDocumentClick, true);
    document.addEventListener("keydown", onKeydown);
  });

  onUnmounted(() => {
    document.removeEventListener("click", onDocumentClick, true);
    document.removeEventListener("keydown", onKeydown);
  });

  return { close, toggle };
}
