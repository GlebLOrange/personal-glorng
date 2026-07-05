import { computed, onMounted, onUnmounted, ref, type Ref } from "vue";

const SCROLLABLE_THRESHOLD = 16;
const THIRD = 1 / 3;

/** Scroll progress from 0 (top) to 1 (bottom). */
export function computeScrollProgress(
  scrollY: number,
  scrollHeight: number,
  innerHeight: number,
): number {
  const maxScroll = Math.max(1, scrollHeight - innerHeight);
  return scrollY / maxScroll;
}

/** Whether the document is taller than the viewport. */
export function computeIsScrollable(scrollHeight: number, innerHeight: number): boolean {
  return scrollHeight > innerHeight + SCROLLABLE_THRESHOLD;
}

export function useScrollProgress(): {
  progress: Ref<number>;
  showArrowDown: Ref<boolean>;
  showToTop: Ref<boolean>;
  isScrollable: Ref<boolean>;
} {
  const progress = ref(0);
  const isScrollable = ref(false);
  let rafId = 0;

  function update(): void {
    const { scrollY, innerHeight } = window;
    const scrollHeight = document.documentElement.scrollHeight;
    isScrollable.value = computeIsScrollable(scrollHeight, innerHeight);
    progress.value = isScrollable.value
      ? computeScrollProgress(scrollY, scrollHeight, innerHeight)
      : 0;
  }

  function onScroll(): void {
    if (rafId) return;
    rafId = window.requestAnimationFrame(() => {
      rafId = 0;
      update();
    });
  }

  onMounted(() => {
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
  });

  onUnmounted(() => {
    if (rafId) window.cancelAnimationFrame(rafId);
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("resize", onScroll);
  });

  const showArrowDown = computed(() => isScrollable.value && progress.value < THIRD);
  const showToTop = computed(() => isScrollable.value && progress.value >= THIRD);

  return { progress, showArrowDown, showToTop, isScrollable };
}
