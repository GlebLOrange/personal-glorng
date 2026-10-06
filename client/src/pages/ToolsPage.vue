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

function sortPublicTools(tools: PlatformService[]): PlatformService[] {
  return [...tools].sort((a, b) => {
    const ai = PUBLIC_TILE_ORDER.indexOf(a.slug);
    const bi = PUBLIC_TILE_ORDER.indexOf(b.slug);
    if (ai === -1 && bi === -1) return 0;
    if (ai === -1) return 1;
    if (bi === -1) return -1;
    return ai - bi;
  });
}

const publicTools = computed((): PlatformService[] => {
  const tools = publicToolsAsServices().filter(
    (tool) => !(tool.slug === "expenses" && !isExpensesEnabled()),
  );
  return sortPublicTools(tools);
});

const signedInTools = computed((): PlatformService[] => {
  return PLATFORM_SERVICES.filter((tool) => {
    if (!TOOLS_PAGE_EXTRA_SLUGS.has(tool.slug)) return false;
    if (tool.slug === "expenses" && !isExpensesEnabled()) return false;
    return canAccess(tool.slug);
  });
});

const publicSections = computed(() => groupServicesByCategory(publicTools.value));
const signedInSections = computed(() => groupServicesByCategory(signedInTools.value));

const hasAnyTools = computed(() => publicTools.value.length > 0 || signedInTools.value.length > 0);

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
      Public utilities you can try without signing in — weather, short links, recipes, and more.
    </p>
    <p
      v-if="expensesOffNotice"
      class="mb-4 rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm text-surface-sage"
      role="status"
    >
      Expenses are turned off on this deploy.
    </p>
    <EmptyState v-if="!hasAnyTools" description="no tools available." />
    <template v-else>
      <ToolTileGrid
        v-if="publicSections.length"
        :sections="publicSections"
        :resolve-route="toolRoute"
      />
      <section v-if="signedInSections.length" class="min-w-0">
        <h2 class="text-meta mb-3 uppercase tracking-wider">your tools</h2>
        <ToolTileGrid
          :sections="signedInSections"
          :resolve-route="toolRoute"
          category-heading="h3"
        />
      </section>
    </template>
  </PageShell>
</template>
