<script setup lang="ts">
import { computed } from "vue";

import PageShell from "@/components/layout/PageShell.vue";
import ToolTileGrid from "@/components/tools/ToolTileGrid.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { usePermissions } from "@/composables/usePermissions";
import {
  groupServicesByCategory,
  PLATFORM_SERVICES,
  publicToolsAsServices,
  resolveToolRoute,
  TOOLS_PAGE_EXTRA_SLUGS,
  type PlatformService,
} from "@/platform/services";

const { can, canAccess } = usePermissions();

const tools = computed((): PlatformService[] => {
  const bySlug = new Map<string, PlatformService>();
  for (const tool of publicToolsAsServices()) {
    bySlug.set(tool.slug, tool);
  }
  for (const tool of PLATFORM_SERVICES) {
    if (TOOLS_PAGE_EXTRA_SLUGS.has(tool.slug) && canAccess(tool.slug)) {
      bySlug.set(tool.slug, tool);
    }
  }
  return [...bySlug.values()];
});

const sections = computed(() => groupServicesByCategory(tools.value));

function toolRoute(tool: PlatformService): string {
  return resolveToolRoute(tool, can);
}
</script>

<template>
  <PageShell
    title="tools"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }]"
    back-to="/"
    :narrow="false"
  >
    <EmptyState v-if="tools.length === 0" description="No tools available." />
    <ToolTileGrid v-else :sections="sections" :resolve-route="toolRoute" gap-class="gap-4" />
  </PageShell>
</template>
