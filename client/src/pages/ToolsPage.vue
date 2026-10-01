<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

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
import { isExpensesEnabled } from "@/utils/featureFlags";

/** Prefer demo-strong tools ahead of calculator / password / QR within each category. */
const PUBLIC_TILE_ORDER = [
  "weather",
  "url-shortener",
  "recipes",
  "calculator",
  "password-generator",
  "qr-generator",
];

const route = useRoute();
const { can, canAccess } = usePermissions();

const expensesOffNotice = computed(() => String(route.query.expenses ?? "") === "off");

const tools = computed((): PlatformService[] => {
  const bySlug = new Map<string, PlatformService>();
  for (const tool of publicToolsAsServices()) {
    if (tool.slug === "expenses" && !isExpensesEnabled()) continue;
    bySlug.set(tool.slug, tool);
  }
  for (const tool of PLATFORM_SERVICES) {
    if (tool.slug === "expenses" && !isExpensesEnabled()) continue;
    if (TOOLS_PAGE_EXTRA_SLUGS.has(tool.slug) && canAccess(tool.slug)) {
      bySlug.set(tool.slug, tool);
    }
  }
  return [...bySlug.values()].sort((a, b) => {
    const ai = PUBLIC_TILE_ORDER.indexOf(a.slug);
    const bi = PUBLIC_TILE_ORDER.indexOf(b.slug);
    if (ai === -1 && bi === -1) return 0;
    if (ai === -1) return 1;
    if (bi === -1) return -1;
    return ai - bi;
  });
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
    <p class="text-body mb-4 max-w-3xl">
      These tiles call the same FastAPI as the portfolio — live routes, auth, and workers on this
      site.
    </p>
    <p
      v-if="expensesOffNotice"
      class="mb-4 rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm text-surface-sage"
      role="status"
    >
      Expenses are turned off on this deploy.
    </p>
    <EmptyState v-if="tools.length === 0" description="no tools available." />
    <ToolTileGrid v-else :sections="sections" :resolve-route="toolRoute" gap-class="gap-4" />
  </PageShell>
</template>
