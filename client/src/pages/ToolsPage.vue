<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import ToolIcon from "@/components/icons/ToolIcon.vue";
import PageShell from "@/components/layout/PageShell.vue";
import ToolTileGrid from "@/components/tools/ToolTileGrid.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { usePermissions } from "@/composables/usePermissions";
import { visibleSmallToolTabs } from "@/constants/smallToolTabs";
import { actionFamilyClass, FOCUS_RING_DEFAULT } from "@/constants/httpStatusColors";
import { publicTileBlurbForSlug } from "@/constants/toolIntros";
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
const router = useRouter();
const { can, canAccess, isSuperuser } = usePermissions();

type NoticeKey = "expenses" | "aichat" | "access";

/** Redirect notices (`?expenses=off`, `?aichat=off`, `?access=denied`). */
const NOTICES: { key: NoticeKey; value: string; text: string }[] = [
  { key: "expenses", value: "off", text: "Expenses are turned off on this deploy." },
  { key: "aichat", value: "off", text: "AI chat is turned off on this deploy." },
  {
    key: "access",
    value: "denied",
    text: "You do not have access to that admin tool. Pick something below, or ask the site owner.",
  },
];

const activeNotices = computed(() =>
  NOTICES.filter((notice) => String(route.query[notice.key] ?? "") === notice.value),
);

function dismissNotice(key: NoticeKey): void {
  const query = { ...route.query };
  delete query[key];
  void router.replace({ query });
}

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

/** Utils catalog pills — each opens a standalone PageShell page. */
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
  () => showUtilsSection.value || tileSections.value.some((section) => section.services.length > 0),
);

function toolRoute(tool: PlatformService): string {
  return resolveToolRoute(tool, can);
}

function sectionCount(section: ToolsPageSection): number {
  return section.services.length;
}

const SUMMARY_CLASS = `flex min-h-11 cursor-pointer list-none items-center gap-2 rounded-lg px-3 py-2 outline-none focus-visible:ring-2 ${FOCUS_RING_DEFAULT} [&::-webkit-details-marker]:hidden`;

const DETAILS_CLASS = "group rounded-lg border border-transparent bg-surface-card/40";

function countLabel(count: number): string {
  return count === 1 ? "1 tool" : `${count} tools`;
}

function tabPillClass(): string {
  return actionFamilyClass("1xx", false);
}
</script>

<template>
  <!-- Casing: lowercase labels are the site voice (nav, breadcrumbs, pills); notices stay sentence case. -->
  <PageShell
    title="tools"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }]"
    back-to="/"
    body-width="column"
  >
    <div
      v-for="notice in activeNotices"
      :key="notice.key"
      class="mb-4 flex items-start gap-2 rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm text-surface-sage"
      role="status"
      :data-notice="notice.key"
    >
      <p class="min-w-0 flex-1">{{ notice.text }}</p>
      <button
        type="button"
        class="-my-1 -mr-1 grid size-8 shrink-0 place-items-center rounded-md text-text-muted outline-none hover:text-surface-light focus-visible:ring-2"
        :class="FOCUS_RING_DEFAULT"
        aria-label="dismiss notice"
        @click="dismissNotice(notice.key)"
      >
        <span aria-hidden="true">×</span>
      </button>
    </div>
    <EmptyState v-if="!hasAnyTools" description="no tools available right now.">
      <template #action>
        <RouterLink
          to="/"
          class="inline-flex min-h-11 items-center rounded-lg bg-accent-coral px-4 text-sm font-semibold text-on-accent outline-none focus-visible:ring-2"
          :class="FOCUS_RING_DEFAULT"
          >back to portfolio</RouterLink
        >
      </template>
    </EmptyState>
    <div v-else class="space-y-3">
      <details v-if="showUtilsSection" id="utils" open :class="DETAILS_CLASS">
        <summary :class="SUMMARY_CLASS">
          <span
            class="inline-block text-surface-mid transition-transform duration-200 group-open:rotate-90"
            aria-hidden="true"
            >▸</span
          >
          <h2 class="text-sm font-semibold text-surface-light">
            <span aria-hidden="true">utils</span>
            <span class="sr-only">utils, {{ countLabel(utilsSectionCount) }}</span>
          </h2>
          <span class="ml-auto text-xs font-medium text-text-muted" aria-hidden="true">{{
            utilsSectionCount
          }}</span>
        </summary>
        <nav class="border-t border-surface-border px-3 pb-3 pt-3" aria-label="utils tools">
          <ul class="flex list-none flex-wrap justify-start gap-2 p-0">
            <li v-for="tab in utilsTabs" :key="tab.id">
              <RouterLink
                :to="tab.to"
                :class="tabPillClass()"
                :title="publicTileBlurbForSlug(tab.id)"
              >
                <ToolIcon :slug="tab.id" class="size-3.5 shrink-0" />
                {{ tab.label }}
                <span v-if="publicTileBlurbForSlug(tab.id)" class="sr-only"
                  >— {{ publicTileBlurbForSlug(tab.id) }}</span
                >
              </RouterLink>
            </li>
          </ul>
        </nav>
      </details>
      <details
        v-for="section in tileSections"
        :id="section.category"
        :key="section.category"
        open
        :class="DETAILS_CLASS"
      >
        <summary :class="SUMMARY_CLASS">
          <span
            class="inline-block text-surface-mid transition-transform duration-200 group-open:rotate-90"
            aria-hidden="true"
            >▸</span
          >
          <h2 class="text-sm font-semibold text-surface-light">
            <span aria-hidden="true">{{ section.label }}</span>
            <span class="sr-only"
              >{{ section.label }}, {{ countLabel(sectionCount(section)) }}</span
            >
          </h2>
          <span class="ml-auto text-xs font-medium text-text-muted" aria-hidden="true">{{
            sectionCount(section)
          }}</span>
        </summary>
        <div class="border-t border-surface-border px-3 pb-3 pt-3">
          <ToolTileGrid
            presentation="public"
            :sections="[section]"
            :show-category-headings="false"
            :section-ids="false"
            :resolve-route="toolRoute"
            :tile-chip="toolsPageChipForSlug"
          />
        </div>
      </details>
    </div>
  </PageShell>
</template>
