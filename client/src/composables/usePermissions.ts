import { computed } from "vue";

import { useAuthStore } from "@/stores/auth";
import { isAiChatEnabled } from "@/utils/featureFlags";
import { permissionKey, SUPERUSER_PERMISSION } from "@/utils/permissions";

/** Slugs that unlock the /admin hub (nav + dashboard). */
export const ADMIN_HUB_SLUGS = [
  "feedback",
  "audit",
  "app-logs",
  "search",
  "email",
  "ai-chat",
  "api-docs",
] as const;

export function usePermissions() {
  const auth = useAuthStore();

  const permissions = computed(() => auth.user?.permissions ?? []);

  const isSuperuser = computed(() => permissions.value.includes(SUPERUSER_PERMISSION));

  function can(slug: string, capability = "read"): boolean {
    if (isSuperuser.value) return true;
    return permissions.value.includes(permissionKey(slug, capability));
  }

  function canAccess(slug: string): boolean {
    return can(slug, "read") || can(slug, "write");
  }

  const canUseAdminHub = computed(() => {
    if (!auth.isAuthenticated) return false;
    if (isSuperuser.value) return true;
    return ADMIN_HUB_SLUGS.some((slug) => {
      if (slug === "ai-chat" && !isAiChatEnabled()) return false;
      if (slug === "api-docs") return false;
      return canAccess(slug);
    });
  });

  return { permissions, isSuperuser, can, canAccess, canUseAdminHub };
}
