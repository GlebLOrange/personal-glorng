import { onUnmounted, watch } from "vue";
import { useRoute } from "vue-router";

import { clearScrollFingerprint, setScrollFingerprint } from "@/utils/scrollRestore";

/**
 * Keep volatile-route scroll fingerprint in sync with list state.
 * Call from pages with sort/filter/pagination that can re-order content.
 */
export function useScrollListFingerprint(getFingerprint: () => string): void {
  const route = useRoute();

  function sync(): void {
    setScrollFingerprint(route.fullPath, getFingerprint());
  }

  watch(() => getFingerprint(), sync, { immediate: true });

  onUnmounted(() => {
    clearScrollFingerprint(route.fullPath);
  });
}
