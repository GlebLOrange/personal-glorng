import { computed } from "vue";

import { useAuthStore } from "@/stores/auth";

const SUPERUSER = "platform:superuser";

export function usePermissions() {
  const auth = useAuthStore();

  const permissions = computed(() => auth.user?.permissions ?? []);

  const isSuperuser = computed(() => permissions.value.includes(SUPERUSER));

  function can(slug: string, capability = "read"): boolean {
    if (isSuperuser.value) return true;
    return permissions.value.includes(`${slug}:${capability}`);
  }

  return { permissions, isSuperuser, can };
}
