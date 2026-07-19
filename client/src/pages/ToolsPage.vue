<script setup lang="ts">
import { computed } from "vue";

import PageShell from "@/components/layout/PageShell.vue";
import { Card } from "@/components/ui/card";
import { usePermissions } from "@/composables/usePermissions";
import {
  groupServicesByCategory,
  publicToolsAsServices,
  resolveToolRoute,
  type PlatformService,
} from "@/platform/services";

const { can } = usePermissions();
const sections = computed(() => groupServicesByCategory(publicToolsAsServices()));

function toolRoute(tool: PlatformService): string {
  return resolveToolRoute(tool, can);
}
</script>

<template>
  <PageShell title="tools" :breadcrumbs="[{ label: 'tools' }]" :narrow="false">
    <section v-for="section in sections" :key="section.category" class="mb-10 min-w-0">
      <h2 class="text-lg font-bold text-surface-light mb-4">{{ section.label }}</h2>
      <div class="page-tool-grid gap-4">
        <RouterLink
          v-for="tool in section.services"
          :key="tool.slug"
          :to="toolRoute(tool)"
          class="page-tile"
        >
          <Card hoverable class="page-tile-card h-full">
            <div class="text-2xl mb-3">{{ tool.icon }}</div>
            <h3 class="text-surface-light font-bold mb-1 break-words">{{ tool.name }}</h3>
            <p class="text-xs text-surface-mid break-words">{{ tool.description }}</p>
          </Card>
        </RouterLink>
      </div>
    </section>
  </PageShell>
</template>
