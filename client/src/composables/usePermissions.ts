import { computed } from "vue";

import { useAuthStore } from "@/stores/auth";
import { permissionKey, SUPERUSER_PERMISSION } from "@/utils/permissions";

export function usePermissions() {
  const auth = useAuthStore();

  const permissions = computed(() => auth.user?.permissions ?? []);

  const isSuperuser = computed(() => permissions.value.includes(SUPERUSER_PERMISSION));

  function can(slug: string, capability = "read"): boolean {
    if (isSuperuser.value) return true;
    return permissions.value.includes(permissionKey(slug, capability));
  }

  return { permissions, isSuperuser, can };
}
