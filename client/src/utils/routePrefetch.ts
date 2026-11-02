import type { RouteLocationRaw, Router } from "vue-router";

const prefetched = new Set<string>();

/** Warm lazy route chunks (`component: () => import(...)`) on hover/focus. No-op once per path. */
export function prefetchRoute(router: Pick<Router, "resolve">, to: RouteLocationRaw): void {
  let resolved;
  try {
    resolved = router.resolve(to);
  } catch {
    return;
  }
  if (prefetched.has(resolved.path)) return;
  prefetched.add(resolved.path);
  for (const record of resolved.matched) {
    for (const component of Object.values(record.components ?? {})) {
      if (typeof component === "function" && !("displayName" in component) && component.length === 0) {
        void Promise.resolve()
          .then(() => (component as () => unknown)())
          .catch(() => prefetched.delete(resolved.path));
      }
    }
  }
}

/** Test hook. */
export function resetRoutePrefetchCache(): void {
  prefetched.clear();
}
