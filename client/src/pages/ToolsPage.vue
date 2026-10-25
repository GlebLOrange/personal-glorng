<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import ToolTileGrid from "@/components/tools/ToolTileGrid.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { usePermissions } from "@/composables/usePermissions";
import {
  PLATFORM_SERVICES,
  publicToolsAsServices,
  resolveToolRoute,
  TOOLS_PAGE_EXTRA_SLUGS,
  type PlatformService,
} from "@/platform/services";
import { isExpensesEnabled } from "@/utils/featureFlags";
import {
  groupServicesForToolsPage,
  toolsPageChipForSlug,
} from "@/utils/toolsPageGroups";

const route = useRoute();
const { can, canAccess } = usePermissions();

const expensesOffNotice = computed(() => String(route.query.expenses ?? "") === "off");

const catalogTools = computed((): PlatformService[] => {
  const publicTools = publicToolsAsServices().filter(
    (tool) => !(tool.slug === "expenses" && !isExpensesEnabled()),
  );
  const extras = PLATFORM_SERVICES.filter((tool) => {
    if (!TOOLS_PAGE_EXTRA_SLUGS.has(tool.slug)) return false;
    if (tool.slug === "expenses" && !isExpensesEnabled()) return false;
    return canAccess(tool.slug);
  });
  return [...publicTools, ...extras];
});

const sections = computed(() => groupServicesForToolsPage(catalogTools.value));

const hasAnyTools = computed(() => sections.value.some((section) => section.services.length > 0));

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
    <p
      v-if="expensesOffNotice"
      class="mb-4 rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm text-surface-sage"
      role="status"
    >
      Expenses are turned off on this deploy.
    </p>
    <EmptyState v-if="!hasAnyTools" description="no tools available." />
    <ToolTileGrid
      v-else
      presentation="public"
      :sections="sections"
      :resolve-route="toolRoute"
      :tile-chip="toolsPageChipForSlug"
    />
  </PageShell>
</template>
