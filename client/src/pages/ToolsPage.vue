<script setup lang="ts">
import { computed } from "vue";

import PageShell from "@/components/layout/PageShell.vue";
import ToolIcon from "@/components/icons/ToolIcon.vue";
import { Card } from "@/components/ui/card";
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
    <section v-for="section in sections" :key="section.category" class="mb-10 min-w-0">
      <h2 class="text-meta mb-4 uppercase tracking-wider">{{ section.label }}</h2>
      <div class="page-tool-grid gap-4">
        <RouterLink
          v-for="tool in section.services"
          :key="tool.slug"
          :to="toolRoute(tool)"
          class="page-tile"
        >
          <Card hoverable class="page-tile-card h-full">
            <ToolIcon :slug="tool.slug" class="mb-3 h-8 w-8 text-surface-light" />
            <h3 class="text-surface-light font-bold mb-1 break-words">{{ tool.name }}</h3>
            <p class="text-xs text-surface-mid break-words">{{ tool.description }}</p>
          </Card>
        </RouterLink>
      </div>
    </section>
  </PageShell>
</template>
