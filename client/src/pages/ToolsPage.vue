<script setup lang="ts">
import { computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import AdminTabBar, { type AdminTab } from "@/components/admin/AdminTabBar.vue";
import PageShell from "@/components/layout/PageShell.vue";
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";
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
import { resolveToolsCategory } from "@/utils/toolsCategory";

const route = useRoute();
const router = useRouter();
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

const availableCategories = computed(() => sections.value.map((section) => section.category));

const categoryTabs = computed((): AdminTab[] =>
  sections.value.map((section) => ({
    id: section.category,
    label: section.label,
  })),
);

const activeCategory = computed({
  get: (): string => resolveToolsCategory(route.query.category, availableCategories.value),
  set: (category: string): void => {
    if (!availableCategories.value.includes(category)) return;
    if (route.query.category === category) return;
    void router.replace({ query: { ...route.query, category } });
  },
});

watch(
  [availableCategories, () => route.query.category],
  () => {
    const resolved = resolveToolsCategory(route.query.category, availableCategories.value);
    if (!resolved || route.query.category === resolved) return;
    void router.replace({ query: { ...route.query, category: resolved } });
  },
  { immediate: true },
);

const activeSections = computed(() =>
  sections.value.filter((section) => section.category === activeCategory.value),
);

const breadcrumbs = computed((): BreadcrumbSegment[] => {
  const crumbs: BreadcrumbSegment[] = [{ label: "tools", to: "/tools" }];
  const category = activeCategory.value;
  if (!category) return crumbs;
  const section = sections.value.find((item) => item.category === category);
  crumbs.push({ label: section?.label ?? category });
  return crumbs;
});

function toolRoute(tool: PlatformService): string {
  return resolveToolRoute(tool, can);
}
</script>

<template>
  <PageShell title="tools" :breadcrumbs="breadcrumbs" back-to="/" :narrow="false">
    <EmptyState v-if="tools.length === 0" description="No tools available." />
    <template v-else>
      <div class="mb-8">
        <AdminTabBar
          v-model="activeCategory"
          :tabs="categoryTabs"
          panel-id-prefix="tools-category"
          aria-label="Tool categories"
          flush
        />
      </div>
      <div
        :id="`tools-category-panel-${activeCategory}`"
        role="tabpanel"
        :aria-labelledby="`tools-category-tab-${activeCategory}`"
      >
        <ToolTileGrid
          :sections="activeSections"
          :resolve-route="toolRoute"
          :show-category-headings="false"
          gap-class="gap-4"
        />
      </div>
    </template>
  </PageShell>
</template>
