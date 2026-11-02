import { onBeforeUnmount, onMounted, type Ref } from "vue";

export const PAGE_CHROME_H_VAR = "--page-chrome-h";

/**
 * Publish the chrome root's rendered height as `--page-chrome-h` on <html>.
 * ResizeObserver keeps it right when breadcrumbs wrap; cleared on unmount only if still ours.
 */
export function usePageChromeHeight(el: Ref<HTMLElement | null>): void {
  let observer: ResizeObserver | null = null;
  let written: string | null = null;

  function publish(): void {
    const node = el.value;
    if (!node) return;
    const height = Math.round(node.getBoundingClientRect().height);
    if (height <= 0) return;
    written = `${height}px`;
    document.documentElement.style.setProperty(PAGE_CHROME_H_VAR, written);
  }

  onMounted(() => {
    publish();
    if (typeof ResizeObserver === "function" && el.value) {
      observer = new ResizeObserver(publish);
      observer.observe(el.value);
    }
  });

  onBeforeUnmount(() => {
    observer?.disconnect();
    observer = null;
    const root = document.documentElement.style;
    // Next page's chrome may already have written its own value during the transition.
    if (written && root.getPropertyValue(PAGE_CHROME_H_VAR) === written) {
      root.removeProperty(PAGE_CHROME_H_VAR);
    }
  });
}
