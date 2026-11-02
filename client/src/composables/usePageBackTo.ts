import { onBeforeUnmount, shallowRef, watch, type Ref } from "vue";
import type { RouteLocationRaw } from "vue-router";

/** Shared Back target for the single bottom chrome rail (ScrollControls renders it). */
const backTo = shallowRef<RouteLocationRaw | undefined>(undefined);

export function usePageBackTo() {
  return { backTo };
}

/** Register a page's Back target while mounted; clears on unmount if still owned. */
export function provideRailBackTo(source: Ref<RouteLocationRaw | undefined>) {
  let owned: RouteLocationRaw | undefined;
  watch(
    source,
    (to) => {
      owned = to;
      backTo.value = to;
    },
    { immediate: true },
  );
  onBeforeUnmount(() => {
    if (backTo.value === owned) backTo.value = undefined;
  });
}
