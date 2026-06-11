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
