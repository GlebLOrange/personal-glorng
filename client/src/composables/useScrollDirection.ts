import { onBeforeUnmount, onMounted, ref } from "vue";

export type UseScrollDirectionOptions = {
  hideAfterY?: number;
  deltaThreshold?: number;
  disabled?: () => boolean;
};

export function useScrollDirection(options: UseScrollDirectionOptions = {}): {
  isHidden: Readonly<{ value: boolean }>;
} {
  const hideAfterY = options.hideAfterY ?? 80;
  const deltaThreshold = options.deltaThreshold ?? 6;
  const isHidden = ref(false);

  let lastScrollY = 0;
  let ticking = false;

  function onScroll(): void {
    if (ticking) return;
    ticking = true;

    window.requestAnimationFrame(() => {
      if (options.disabled?.()) {
        isHidden.value = false;
        lastScrollY = window.scrollY;
        ticking = false;
        return;
      }

      const y = window.scrollY;
      const delta = y - lastScrollY;

      // ponytail: simple hide/show heuristic; upgrade path is IntersectionObserver sentinel.
      if (y > hideAfterY && delta > deltaThreshold) isHidden.value = true;
      if (delta < -deltaThreshold) isHidden.value = false;

      lastScrollY = y;
      ticking = false;
    });
  }

  onMounted(() => {
    lastScrollY = window.scrollY;
    window.addEventListener("scroll", onScroll, { passive: true });
  });

  onBeforeUnmount(() => {
    window.removeEventListener("scroll", onScroll);
  });

  return { isHidden };
}

