import { onUnmounted, watch, type WatchSource } from "vue";

/** Ref-count body scroll locks so stacked modals/drawers don't unlock early. */
let lockCount = 0;
let previousOverflow = "";

function applyLock(): void {
  if (lockCount === 0) {
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
  }
  lockCount += 1;
}

function releaseLock(): void {
  if (lockCount === 0) return;
  lockCount -= 1;
  if (lockCount === 0) {
    document.body.style.overflow = previousOverflow;
  }
}

/**
 * Lock document body scroll while `source` is true.
 * Safe for stacked overlays via a process-wide ref count.
 */
export function useScrollLock(source: WatchSource<boolean>): void {
  let holding = false;

  watch(
    source,
    (shouldLock) => {
      if (shouldLock && !holding) {
        applyLock();
        holding = true;
        return;
      }
      if (!shouldLock && holding) {
        releaseLock();
        holding = false;
      }
    },
    { immediate: true },
  );

  onUnmounted(() => {
    if (holding) {
      releaseLock();
      holding = false;
    }
  });
}
