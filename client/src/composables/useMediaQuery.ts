import { onMounted, onUnmounted, ref, type Ref } from "vue";

function readMatches(query: string): boolean {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return false;
  }
  return window.matchMedia(query).matches;
}

/**
 * Reactive `window.matchMedia` result.
 * Reads immediately on the client (avoids a one-frame wrong default), stays `false` when
 * `window` is unavailable.
 */
export function useMediaQuery(query: string): Ref<boolean> {
  const matches = ref(readMatches(query));

  onMounted(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
      return;
    }
    const media = window.matchMedia(query);
    const sync = () => {
      matches.value = media.matches;
    };
    sync();
    media.addEventListener("change", sync);
    onUnmounted(() => media.removeEventListener("change", sync));
  });

  return matches;
}
