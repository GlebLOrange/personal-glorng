export async function restoreAuth(): Promise<void> {
  const { useAuthStore } = await import("@/stores/auth");
  const auth = useAuthStore();
  if (auth.sessionResolved) return;
  try {
    await auth.resolveSession();
  } catch {
    // sessionError is set in the store; app still mounts
  }
}
