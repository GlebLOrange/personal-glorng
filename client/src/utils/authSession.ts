/** Attempt cookie refresh; clear session and redirect on failure. */
export async function tryRefreshSession(): Promise<boolean> {
  try {
    const { api } = await import("@/composables/useApi");
    await api.post("/auth/refresh");
    return true;
  } catch {
    await handleAuthFailure();
    return false;
  }
}

/** Clear client session state after refresh failure or forced sign-out. */
export async function handleAuthFailure(): Promise<void> {
  const { useAuthStore } = await import("@/stores/auth");
  useAuthStore().clearUser();

  const { default: router } = await import("@/router");
  const route = router.currentRoute.value;
  const needsAuth = Boolean(route.meta.requiresAuth || route.meta.requiresSuperuser);
  if (needsAuth && route.path !== "/login") {
    await router.replace({
      path: "/login",
      query: { redirect: route.fullPath },
    });
  }
}
