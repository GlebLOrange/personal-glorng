import { computed, ref, type ComputedRef } from "vue";

import { api } from "@/composables/useApi";
import { PLATFORM_SERVICES, type PlatformService } from "@/platform/services";
import { useAuthStore } from "@/stores/auth";
import { isAiChatEnabled, isExpensesEnabled } from "@/utils/featureFlags";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";
import { safeNavigationHref } from "@/utils/safeUrl";

type ApiPlatformService = {
  slug: string;
  name: string;
  category: string;
  category_label: string;
  description: string;
  api_prefix: string;
  admin_route: string;
  icon: string;
  capabilities: string[];
  external: boolean;
  public?: boolean;
  public_route?: string | null;
};

/** Unfiltered catalog; AI-chat visibility is derived in usePlatformCatalog. */
const rawServices = ref<PlatformService[]>(PLATFORM_SERVICES);
const loaded = ref(false);
let loadPromise: Promise<void> | null = null;

function filterAiChat(services: PlatformService[]): PlatformService[] {
  const auth = useAuthStore();
  const isSuperuser = auth.user?.permissions.includes(SUPERUSER_PERMISSION) ?? false;
  if (isAiChatEnabled() && isSuperuser) return services;
  return services.filter((s) => s.slug !== "ai-chat");
}

function filterDisabledServices(services: PlatformService[]): PlatformService[] {
  if (isExpensesEnabled()) return services;
  return services.filter((s) => s.slug !== "expenses");
}

/**
 * Map an API catalog row into a PlatformService, or null when admin_route is unsafe.
 * public_route is cleared (not dropped) when unsafe.
 */
export function mapApiPlatformService(s: ApiPlatformService): PlatformService | null {
  const adminRoute = safeNavigationHref(s.admin_route);
  if (!adminRoute) return null;

  const publicRaw = s.public_route?.trim();
  const publicRoute = publicRaw ? (safeNavigationHref(publicRaw) ?? undefined) : undefined;

  return {
    slug: s.slug,
    name: s.name,
    category: s.category,
    categoryLabel: s.category_label,
    description: s.description,
    apiPrefix: s.api_prefix,
    adminRoute,
    icon: s.icon,
    capabilities: s.capabilities,
    external: s.external,
    public: s.public,
    publicRoute,
  };
}

/** Reset module cache (call on logout so the next session can refetch). */
export function clearPlatformCatalog(): void {
  loaded.value = false;
  loadPromise = null;
  rawServices.value = PLATFORM_SERVICES;
}

/** Load platform catalog from API with static fallback (module-level cache). */
export function usePlatformCatalog(): {
  services: ComputedRef<PlatformService[]>;
  load: () => Promise<void>;
} {
  // Derive when a Vue/Pinia context exists (not at module import time).
  const services = computed(() => filterDisabledServices(filterAiChat(rawServices.value)));

  async function load(): Promise<void> {
    if (loaded.value) return;
    if (!loadPromise) {
      loadPromise = (async () => {
        try {
          const { data } = await api.get<{
            services: ApiPlatformService[];
          }>("/platform/catalog");
          rawServices.value = data.services
            .map(mapApiPlatformService)
            .filter((service): service is PlatformService => service !== null);
        } catch {
          rawServices.value = PLATFORM_SERVICES;
        } finally {
          loaded.value = true;
        }
      })();
    }
    await loadPromise;
  }

  return { services, load };
}
