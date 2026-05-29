<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import WeatherCard from "@/components/weather/WeatherCard.vue";
import { api } from "@/composables/useApi";
import {
  groupServicesByCategory,
  PLATFORM_SERVICES,
  type PlatformService,
} from "@/platform/services";
import { useAuthStore } from "@/stores/auth";
import { isAiChatEnabled } from "@/utils/featureFlags";

function filterAiChat(services: PlatformService[]): PlatformService[] {
  if (isAiChatEnabled()) return services;
  return services.filter((s) => s.slug !== "ai-chat");
}

const auth = useAuthStore();
const services = ref<PlatformService[]>(filterAiChat(PLATFORM_SERVICES));

const sections = computed(() => groupServicesByCategory(services.value));

onMounted(async () => {
  try {
    const { data } = await api.get<{
      services: Array<{
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
      }>;
    }>("/platform/services");
    services.value = data.services.map((s) => ({
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
    }));
  } catch {
    // Fallback to static registry
  }
});
</script>

<template>
  <AdminPageLayout title="tools" max-width="xl">
    <div class="mb-6">
      <p class="text-surface-mid text-sm mb-2">
        Welcome back, {{ auth.user?.email ?? "admin" }}
      </p>
      <p class="text-surface-muted text-xs">
        Services shared across web, bot, and workers
      </p>
    </div>

    <section v-for="section in sections" :key="section.category" class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">{{ section.label }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <WeatherCard v-if="section.category === 'utilities'" />
        <component
          v-for="tool in section.services"
          :key="tool.adminRoute"
          :is="tool.external ? 'a' : 'RouterLink'"
          :to="tool.external ? undefined : tool.adminRoute"
          :href="tool.external ? tool.adminRoute : undefined"
          :target="tool.external ? '_blank' : undefined"
          :rel="tool.external ? 'noopener' : undefined"
        >
          <BaseCard hoverable class="h-full">
            <div class="text-2xl mb-3">{{ tool.icon }}</div>
            <h3 class="text-surface-light font-bold mb-1">{{ tool.name }}</h3>
            <p class="text-xs text-surface-mid">{{ tool.description }}</p>
          </BaseCard>
        </component>
      </div>
    </section>
  </AdminPageLayout>
</template>
