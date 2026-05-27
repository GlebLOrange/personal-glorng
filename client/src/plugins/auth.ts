import { useAuthStore } from "@/stores/auth";

export async function restoreAuth(): Promise<void> {
  const auth = useAuthStore();
  if (auth.accessToken) {
    await auth.fetchUser();
  }
}
