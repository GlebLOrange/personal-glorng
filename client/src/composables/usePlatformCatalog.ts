import { ref, type Ref } from "vue";

import { api } from "@/composables/useApi";
import { PLATFORM_SERVICES, type PlatformCatalog, type PlatformService } from "@/platform/services";
import { useAuthStore } from "@/stores/auth";
import { isAiChatEnabled } from "@/utils/featureFlags";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";

function filterAiChat(services: PlatformService[]): PlatformService[] {
  const auth = useAuthStore();
  const isSuperuser = auth.user?.permissions.includes(SUPERUSER_PERMISSION) ?? false;
  if (isAiChatEnabled() && isSuperuser) return services;
  return services.filter((s) => s.slug !== "ai-chat");
}

function mapApiService(s: PlatformCatalog["services"][number]): PlatformService {
  return {
    slug: s.slug,
    name: s.name,
    category: s.category,
    categoryLabel: s.categoryLabel,
    description: s.description,
    apiPrefix: s.apiPrefix,
    adminRoute: s.adminRoute,
    icon: s.icon,
    capabilities: s.capabilities,
    external: s.external,
    public: s.public,
    publicRoute: s.publicRoute,
  };
}

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

const services = ref<PlatformService[]>(filterAiChat(PLATFORM_SERVICES));
const loaded = ref(false);
let loadPromise: Promise<void> | null = null;

/** Load platform catalog from API with static fallback (module-level cache). */
export function usePlatformCatalog(): {
  services: Ref<PlatformService[]>;
  load: () => Promise<void>;
} {
  async function load(): Promise<void> {
    if (loaded.value) {
      services.value = filterAiChat(services.value);
      return;
    }
    if (!loadPromise) {
      loadPromise = (async () => {
        try {
          const { data } = await api.get<{
            services: ApiPlatformService[];
          }>("/platform/catalog");
          services.value = filterAiChat(
            data.services.map((s) =>
              mapApiService({
                slug: s.slug,
                name: s.name,
                category: s.category,
                categoryLabel: s.category_label,
                description: s.description,
                apiPrefix: s.api_prefix,
                adminRoute: s.admin_route,
                icon: s.icon,
                capabilities: s.capabilities,
                external: s.external,
                public: s.public,
                publicRoute: s.public_route ?? undefined,
              }),
            ),
          );
        } catch {
          services.value = filterAiChat(PLATFORM_SERVICES);
        } finally {
          loaded.value = true;
        }
      })();
    }
    await loadPromise;
  }

  return { services, load };
}
