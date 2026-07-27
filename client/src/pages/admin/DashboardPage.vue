<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import ToolTileGrid from "@/components/tools/ToolTileGrid.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import { usePlatformCatalog } from "@/composables/usePlatformCatalog";
import { ADMIN_HUB_SERVICE_SLUGS, groupServicesByCategory } from "@/platform/services";
import { usePermissions } from "@/composables/usePermissions";
import { isAiChatEnabled } from "@/utils/featureFlags";

const { canAccess, isSuperuser } = usePermissions();
const { services, load } = usePlatformCatalog();
const catalogLoading = ref(true);

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

onMounted(async () => {
  try {
    await load();
  } finally {
    catalogLoading.value = false;
  }
});
</script>

<template>
  <AdminPageLayout title="admin" max-width="xl" back-to="/">
    <div v-if="catalogLoading" aria-busy="true" aria-label="loading tools">
      <section v-for="block in 2" :key="block" class="mb-8 min-w-0">
        <div class="mb-3 h-3 w-24 animate-pulse rounded bg-surface-card" aria-hidden="true" />
        <div class="page-tool-grid">
          <Card
            v-for="i in 3"
            :key="`${block}-${i}`"
            class="page-tile-card min-h-36 animate-pulse sm:min-h-40"
          />
        </div>
      </section>
    </div>
    <EmptyState
      v-else-if="sections.length === 0"
      title="no tools available"
      description="contact an admin if you need access."
    />
    <ToolTileGrid v-else density="compact" :sections="sections" />
  </AdminPageLayout>
</template>
