import { useAuthStore } from "@/stores/auth";

export async function restoreAuth(): Promise<void> {
  const auth = useAuthStore();
  await auth.fetchUser();
}
