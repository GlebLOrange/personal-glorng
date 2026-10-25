<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import ToolTileGrid from "@/components/tools/ToolTileGrid.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { usePermissions } from "@/composables/usePermissions";
import {
  ADMIN_HUB_SERVICE_SLUGS,
  groupAdminHub,
  PLATFORM_SERVICES,
  publicToolsAsServices,
  resolveToolRoute,
  TOOLS_PAGE_EXTRA_SLUGS,
  type PlatformService,
} from "@/platform/services";
import { isAiChatEnabled, isExpensesEnabled } from "@/utils/featureFlags";
import {
  groupServicesForToolsPage,
  toolsPageChipForSlug,
} from "@/utils/toolsPageGroups";

const route = useRoute();
const { can, canAccess, isSuperuser } = usePermissions();

const expensesOffNotice = computed(() => String(route.query.expenses ?? "") === "off");
const aiChatOffNotice = computed(() => String(route.query.aichat ?? "") === "off");
const accessDeniedNotice = computed(() => String(route.query.access ?? "") === "denied");

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

/** Ops hub tiles — only for logged-in superadmin on /tools. */
const adminTools = computed((): PlatformService[] => {
  if (!isSuperuser.value) return [];
  const catalogSlugs = new Set(catalogTools.value.map((tool) => tool.slug));
  return PLATFORM_SERVICES.filter((tool) => {
    if (!ADMIN_HUB_SERVICE_SLUGS.has(tool.slug)) return false;
    if (catalogSlugs.has(tool.slug)) return false;
    if (tool.slug === "ai-chat" && !isAiChatEnabled()) return false;
    return Boolean(tool.adminRoute);
  });
});

const sections = computed(() => groupServicesForToolsPage(catalogTools.value));
/** Prefix hub section ids so they do not collide with catalog ids (e.g. content). */
const adminSections = computed(() =>
  groupAdminHub(adminTools.value).map((section) => ({
    ...section,
    category: `hub-${section.category}`,
  })),
);

const hasAnyTools = computed(
  () =>
    sections.value.some((section) => section.services.length > 0) ||
    adminSections.value.length > 0,
);

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
    <p
      v-if="aiChatOffNotice"
      class="mb-4 rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm text-surface-sage"
      role="status"
    >
      AI chat is turned off on this deploy.
    </p>
    <p
      v-if="accessDeniedNotice"
      class="mb-4 rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm text-surface-sage"
      role="status"
    >
      You do not have access to that admin tool. Pick something below, or ask the site owner.
    </p>
    <EmptyState v-if="!hasAnyTools" description="no tools available." />
    <template v-else>
      <ToolTileGrid
        v-if="sections.length"
        presentation="public"
        :sections="sections"
        :resolve-route="toolRoute"
        :tile-chip="toolsPageChipForSlug"
      />
      <ToolTileGrid
        v-if="adminSections.length"
        presentation="admin"
        density="compact"
        :sections="adminSections"
        :resolve-route="toolRoute"
        category-heading="h3"
      />
    </template>
  </PageShell>
</template>
