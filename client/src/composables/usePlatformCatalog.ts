import { ref, type Ref } from "vue";

import { api } from "@/composables/useApi";
import { PLATFORM_SERVICES, type PlatformCatalog, type PlatformService } from "@/platform/services";
import { isAiChatEnabled } from "@/utils/featureFlags";

function filterAiChat(services: PlatformService[]): PlatformService[] {
  if (isAiChatEnabled()) return services;
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
};

/** Load platform catalog from API with static fallback. */
export function usePlatformCatalog(): {
  services: Ref<PlatformService[]>;
  load: () => Promise<void>;
} {
  const services = ref<PlatformService[]>(filterAiChat(PLATFORM_SERVICES));

  async function load(): Promise<void> {
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
          }),
        ),
      );
    } catch {
      services.value = filterAiChat(PLATFORM_SERVICES);
    }
  }

  return { services, load };
}
