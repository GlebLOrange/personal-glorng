/** Attempt cookie refresh; clear session and redirect on failure. */
let inFlightRefresh: Promise<boolean> | null = null;

async function refreshSessionOnce(): Promise<boolean> {
  try {
    const { api } = await import("@/composables/useApi");
    await api.post("/auth/refresh");
    return true;
  } catch {
    await handleAuthFailure();
    return false;
  }
}

/**
 * Single-flight cookie refresh shared by axios interceptor and streaming fetch.
 * Concurrent callers await the same in-flight attempt.
 */
export async function tryRefreshSession(): Promise<boolean> {
  if (inFlightRefresh) {
    return inFlightRefresh;
  }
  inFlightRefresh = refreshSessionOnce().finally(() => {
    inFlightRefresh = null;
  });
  return inFlightRefresh;
}

/** Clear client session state after refresh failure or forced sign-out. */
export async function handleAuthFailure(): Promise<void> {
  const { useAuthStore } = await import("@/stores/auth");
  useAuthStore().clearUser();

  const { default: router } = await import("@/router");
  const { scrubSensitivePath } = await import("@/utils/sensitiveUrl");
  const route = router.currentRoute.value;
  const needsAuth = Boolean(route.meta.requiresAuth || route.meta.requiresSuperuser);
  if (needsAuth && route.path !== "/login") {
    await router.replace({
      path: "/login",
      query: { redirect: scrubSensitivePath(route.fullPath) },
    });
  }
}
