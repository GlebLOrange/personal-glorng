<script setup lang="ts">
import { computed, onMounted } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import ToolIcon from "@/components/icons/ToolIcon.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import { usePlatformCatalog } from "@/composables/usePlatformCatalog";
import { ADMIN_HUB_SERVICE_SLUGS, groupServicesByCategory } from "@/platform/services";
import { usePermissions } from "@/composables/usePermissions";
import { isAiChatEnabled } from "@/utils/featureFlags";

const { canAccess, isSuperuser } = usePermissions();
const { services, load } = usePlatformCatalog();

const visibleServices = computed(() =>
  services.value.filter((service) => {
    if (!service.adminRoute) return false;
    if (!ADMIN_HUB_SERVICE_SLUGS.has(service.slug)) return false;
    if (service.slug === "ai-chat" && !isAiChatEnabled()) return false;
    if (service.slug === "api-docs") return isSuperuser.value;
    return canAccess(service.slug);
  }),
);

const sections = computed(() => groupServicesByCategory(visibleServices.value));

onMounted(() => load());
</script>

<template>
  <AdminPageLayout title="admin" max-width="xl" back-to="/">
    <EmptyState
      v-if="sections.length === 0"
      title="No tools available"
      description="Contact an admin if you need access."
    />
    <section v-for="section in sections" :key="section.category" class="mb-10 min-w-0">
      <h2 class="text-meta mb-4 uppercase tracking-wider">{{ section.label }}</h2>
      <div class="page-tool-grid">
        <component
          :is="tool.external ? 'a' : 'RouterLink'"
          v-for="tool in section.services"
          :key="tool.slug"
          class="page-tile"
          :to="tool.external ? undefined : tool.adminRoute"
          :href="tool.external ? tool.adminRoute : undefined"
          :target="tool.external ? '_blank' : undefined"
          :rel="tool.external ? 'noopener noreferrer' : undefined"
          :aria-label="tool.external ? `${tool.name} (opens in new tab)` : undefined"
        >
          <Card hoverable class="page-tile-card h-full">
            <ToolIcon :slug="tool.slug" class="mb-3 h-8 w-8 text-surface-light" />
            <h3 class="text-surface-light font-bold mb-1 break-words">
              {{ tool.name }}
              <span v-if="tool.external" class="text-surface-mid font-normal"> ↗</span>
            </h3>
            <p class="text-xs text-surface-mid break-words">{{ tool.description }}</p>
          </Card>
        </component>
      </div>
    </section>
  </AdminPageLayout>
</template>
