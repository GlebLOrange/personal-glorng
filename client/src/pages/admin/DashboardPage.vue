<script setup lang="ts">
import { computed, onMounted } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import { Card } from "@/components/ui/card";
import { usePlatformCatalog } from "@/composables/usePlatformCatalog";
import { groupServicesByCategory } from "@/platform/services";
import { usePermissions } from "@/composables/usePermissions";

const { can, isSuperuser } = usePermissions();
const { services, load } = usePlatformCatalog();

const SUPERUSER_ONLY_SERVICES = new Set(["news"]);

const visibleServices = computed(() =>
  services.value.filter(
    (service) =>
      can(service.slug, "read") &&
      (!SUPERUSER_ONLY_SERVICES.has(service.slug) || isSuperuser.value),
  ),
);

const sections = computed(() => groupServicesByCategory(visibleServices.value));

onMounted(() => load());
</script>

<template>
  <AdminPageLayout title="tools" max-width="xl" back-to="/">
    <div v-if="isSuperuser" class="mb-8 min-w-0">
      <div class="page-tool-grid">
        <RouterLink to="/admin/users" class="page-tile">
          <Card hoverable class="page-tile-card h-full">
            <div class="text-2xl mb-3">👤</div>
            <h3 class="text-surface-light font-bold break-words">users</h3>
          </Card>
        </RouterLink>
      </div>
    </div>

    <section v-for="section in sections" :key="section.category" class="mb-10 min-w-0">
      <h2 class="text-lg font-bold text-surface-light mb-4">{{ section.label }}</h2>
      <div class="page-tool-grid">
        <component
          :is="tool.external ? 'a' : 'RouterLink'"
          v-for="tool in section.services"
          :key="tool.adminRoute"
          class="page-tile"
          :to="tool.external ? undefined : tool.adminRoute"
          :href="tool.external ? tool.adminRoute : undefined"
          :target="tool.external ? '_blank' : undefined"
          :rel="tool.external ? 'noopener' : undefined"
        >
          <Card hoverable class="page-tile-card h-full">
            <div class="text-2xl mb-3">{{ tool.icon }}</div>
            <h3 class="text-surface-light font-bold mb-1 break-words">{{ tool.name }}</h3>
            <p class="text-xs text-surface-mid break-words">{{ tool.description }}</p>
          </Card>
        </component>
      </div>
    </section>
  </AdminPageLayout>
</template>
