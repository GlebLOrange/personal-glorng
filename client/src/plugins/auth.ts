import { useAuthStore } from "@/stores/auth";

export async function restoreAuth(): Promise<void> {
  const auth = useAuthStore();
  try {
    await auth.resolveSession();
  } catch {
    // sessionError is set in the store; app still mounts
  }
}
