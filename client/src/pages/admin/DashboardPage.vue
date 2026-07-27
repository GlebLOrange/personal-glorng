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
    <div v-if="catalogLoading" class="page-tool-grid" aria-busy="true" aria-label="Loading tools">
      <Card v-for="i in 6" :key="i" class="page-tile-card min-h-40 animate-pulse" />
    </div>
    <EmptyState
      v-else-if="sections.length === 0"
      title="No tools available"
      description="Contact an admin if you need access."
    />
    <ToolTileGrid v-else :sections="sections" />
  </AdminPageLayout>
</template>
