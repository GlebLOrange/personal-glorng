<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import ToolTileGrid from "@/components/tools/ToolTileGrid.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import { api } from "@/composables/useApi";
import { usePlatformCatalog } from "@/composables/usePlatformCatalog";
import { ADMIN_HUB_SERVICE_SLUGS, groupServicesByCategory } from "@/platform/services";
import { usePermissions } from "@/composables/usePermissions";
import { isAiChatEnabled } from "@/utils/featureFlags";

const route = useRoute();
const { canAccess, isSuperuser } = usePermissions();
const { services, load } = usePlatformCatalog();
const catalogLoading = ref(true);
const apiHealth = ref<"ok" | "error" | "loading">("loading");

const aiChatOffNotice = computed(() => String(route.query.aichat ?? "") === "off");

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

async function loadHealth(): Promise<void> {
  try {
    const { data } = await api.get<{ status: string }>("/health");
    apiHealth.value = data.status === "ok" ? "ok" : "error";
  } catch {
    apiHealth.value = "error";
  }
}

onMounted(async () => {
  try {
    await Promise.all([load(), loadHealth()]);
  } finally {
    catalogLoading.value = false;
  }
});
</script>

<template>
  <AdminPageLayout title="admin" max-width="5xl" back-to="/">
    <p class="mb-4 text-sm text-surface-mid" role="status">
      API health:
      <span v-if="apiHealth === 'loading'">checking…</span>
      <span v-else-if="apiHealth === 'ok'" class="text-status-success">ok</span>
      <span v-else class="text-status-error">unreachable</span>
    </p>
    <p
      v-if="aiChatOffNotice"
      class="mb-4 rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm text-surface-sage"
      role="status"
    >
      AI chat is turned off on this deploy.
    </p>
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
