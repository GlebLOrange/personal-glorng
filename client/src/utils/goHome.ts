import type { Router } from "vue-router";

function scrollBehavior(): ScrollBehavior {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth";
}

/**
 * Navigate to the portfolio home route, or scroll to top when already there.
 * Clears an in-page hash so section anchors do not keep the viewport pinned.
 */
export async function goHome(router: Router): Promise<void> {
  const { path, hash } = router.currentRoute.value;
  if (path === "/") {
    if (hash) {
      await router.replace({ path: "/" });
    }
    window.scrollTo({ top: 0, behavior: scrollBehavior() });
    return;
  }
  await router.push("/");
}
