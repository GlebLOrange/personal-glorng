<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import ToolTileGrid from "@/components/tools/ToolTileGrid.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { usePermissions } from "@/composables/usePermissions";
import { visibleSmallToolTabs } from "@/constants/smallToolTabs";
import { actionFamilyClass } from "@/constants/httpStatusColors";
import {
  ADMIN_HUB_SERVICE_SLUGS,
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
  type ToolsPageSection,
} from "@/utils/toolsPageGroups";

const route = useRoute();
const { can, canAccess, isSuperuser } = usePermissions();

const expensesOffNotice = computed(() => String(route.query.expenses ?? "") === "off");
const aiChatOffNotice = computed(() => String(route.query.aichat ?? "") === "off");
const accessDeniedNotice = computed(() => String(route.query.access ?? "") === "denied");

/** Public + capability extras + (superuser-only) admin hub tiles — one list, slug-deduped. */
const visibleTools = computed((): PlatformService[] => {
  const bySlug = new Map<string, PlatformService>();

  for (const tool of publicToolsAsServices()) {
    if (tool.slug === "expenses" && !isExpensesEnabled()) continue;
    bySlug.set(tool.slug, tool);
  }

  for (const tool of PLATFORM_SERVICES) {
    if (!TOOLS_PAGE_EXTRA_SLUGS.has(tool.slug)) continue;
    if (tool.slug === "expenses" && !isExpensesEnabled()) continue;
    if (!canAccess(tool.slug)) continue;
    bySlug.set(tool.slug, tool);
  }

  if (isSuperuser.value) {
    for (const tool of PLATFORM_SERVICES) {
      if (!ADMIN_HUB_SERVICE_SLUGS.has(tool.slug)) continue;
      if (tool.slug === "ai-chat" && !isAiChatEnabled()) continue;
      if (!tool.adminRoute) continue;
      if (bySlug.has(tool.slug)) continue;
      bySlug.set(tool.slug, tool);
    }
  }

  return [...bySlug.values()];
});

const sections = computed(() => groupServicesForToolsPage(visibleTools.value));

const tileSections = computed(() =>
  sections.value.filter((section) => section.category !== "utils"),
);

/** Utils tools that open in the compact window. Same visibility as the catalog. */
const utilsTabs = computed(() =>
  visibleSmallToolTabs({
    canAccess,
    isSuperuser: isSuperuser.value,
    aiChatEnabled: isAiChatEnabled(),
  }),
);

const utilsSectionCount = computed(() => utilsTabs.value.length);

const showUtilsSection = computed(() => utilsTabs.value.length > 0);

const hasAnyTools = computed(
  () =>
    showUtilsSection.value ||
    tileSections.value.some((section) => section.services.length > 0),
);

function toolRoute(tool: PlatformService): string {
  return resolveToolRoute(tool, can);
}

function sectionCount(section: ToolsPageSection): number {
  return section.services.length;
}

function tabPillClass(): string {
  return actionFamilyClass("1xx", false);
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
    <div v-else class="space-y-3">
      <section
        v-if="showUtilsSection"
        id="utils"
        class="rounded-lg bg-surface-card/40"
      >
        <div
          class="flex min-h-11 items-center gap-2 px-3 py-2 text-sm font-semibold text-surface-light"
        >
          <span class="inline-block text-surface-mid" aria-hidden="true">•</span>
          <span aria-hidden="true">utils</span>
          <span class="sr-only"
            >utils,
            {{ utilsSectionCount === 1 ? "1 tool" : `${utilsSectionCount} tools` }}</span
          >
          <span class="ml-auto text-xs font-medium text-surface-mid" aria-hidden="true">{{
            utilsSectionCount
          }}</span>
        </div>
        <div class="px-3 pb-3 pt-3">
          <div
            class="flex flex-wrap justify-start gap-2"
            aria-label="utils tools"
          >
            <RouterLink
              v-for="tab in utilsTabs"
              :key="tab.id"
              :to="tab.to"
              :class="tabPillClass()"
            >
              {{ tab.label }}
            </RouterLink>
          </div>
        </div>
      </section>
      <details
        v-for="section in tileSections"
        :id="section.category"
        :key="section.category"
        open
        class="group rounded-lg border border-transparent bg-surface-card/40 open:border-surface-border"
      >
        <summary
          class="flex min-h-11 cursor-pointer list-none items-center gap-2 px-3 py-2 text-sm font-semibold text-surface-light outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50 rounded-lg"
        >
          <span
            class="inline-block text-surface-mid transition-transform duration-200 group-open:rotate-90"
            aria-hidden="true"
            >▸</span
          >
          <span aria-hidden="true">{{ section.label }}</span>
          <span class="sr-only"
            >{{ section.label }},
            {{ sectionCount(section) === 1 ? "1 tool" : `${sectionCount(section)} tools` }}</span
          >
          <span class="ml-auto text-xs font-medium text-surface-mid" aria-hidden="true">{{
            sectionCount(section)
          }}</span>
        </summary>
        <div class="border-t border-surface-border px-3 pb-3 pt-3">
          <ToolTileGrid
            presentation="public"
            :sections="[section]"
            :show-category-headings="false"
            :resolve-route="toolRoute"
            :tile-chip="toolsPageChipForSlug"
          />
        </div>
      </details>
    </div>
  </PageShell>
</template>
