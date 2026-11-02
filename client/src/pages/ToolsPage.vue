<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import ToolIcon from "@/components/icons/ToolIcon.vue";
import PageShell from "@/components/layout/PageShell.vue";
import ToolsCatalogSection from "@/components/tools/ToolsCatalogSection.vue";
import ToolTileGrid from "@/components/tools/ToolTileGrid.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { useMediaQuery } from "@/composables/useMediaQuery";
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
import { prefetchRoute } from "@/utils/routePrefetch";
import {
  groupServicesForToolsPage,
  toolsPageChipForSlug,
  withoutUtilsTabPeers,
  type ToolsPageSection,
} from "@/utils/toolsPageGroups";

const route = useRoute();
const router = useRouter();
const { can, canAccess, isSuperuser } = usePermissions();

/** Mobile / narrow viewport — sections start collapsed until the user opens them. */
const isNarrow = useMediaQuery("(max-width: 767px)");

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
  sections.value
    .filter((section) => section.category !== "utils")
    .map((section) => ({
      ...section,
      // Duplicate remover: utils pills must not also appear as content/server tiles.
      services: withoutUtilsTabPeers(section.services),
    }))
    .filter((section) => section.services.length > 0),
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

/** Manual open overrides; cleared when viewport band changes. */
const sectionOpenOverrides = reactive<Record<string, boolean>>({});

/** Open-state memory per viewport band. */
const OPEN_STORAGE_PREFIX = "tools:open-sections:";

function openStorageKey(): string {
  return `${OPEN_STORAGE_PREFIX}${isNarrow.value ? "narrow" : "wide"}`;
}

function readStoredOpen(): Record<string, boolean> {
  try {
    const raw = sessionStorage.getItem(openStorageKey());
    const parsed: unknown = raw ? JSON.parse(raw) : null;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return {};
    return Object.fromEntries(
      Object.entries(parsed as Record<string, unknown>).filter(
        (entry): entry is [string, boolean] =>
          /^[a-z0-9-]{1,32}$/.test(entry[0]) && typeof entry[1] === "boolean",
      ),
    );
  } catch {
    return {};
  }
}

function persistOpen(): void {
  try {
    sessionStorage.setItem(openStorageKey(), JSON.stringify({ ...sectionOpenOverrides }));
  } catch {
    /* storage full / disabled — memory is best-effort */
  }
}

function resetOverrides(): void {
  for (const key of Object.keys(sectionOpenOverrides)) {
    delete sectionOpenOverrides[key];
  }
  Object.assign(sectionOpenOverrides, readStoredOpen());
}

watch(isNarrow, resetOverrides);
resetOverrides();

function defaultSectionOpen(id: string): boolean {
  // Desktop: all open. Mobile: utils open (quick pills), the rest collapsed.
  return !isNarrow.value || id === "utils";
}

function isSectionOpen(id: string): boolean {
  if (id in sectionOpenOverrides) return sectionOpenOverrides[id]!;
  return defaultSectionOpen(id);
}

/** All rendered section ids (utils first) — used to validate #hash jumps. */
const sectionIds = computed((): string[] => [
  ...(showUtilsSection.value ? ["utils"] : []),
  ...tileSections.value.map((section) => section.category),
]);

function onSectionToggle(id: string, open: boolean): void {
  if (open === isSectionOpen(id)) return; // native toggle echo of a controlled change
  sectionOpenOverrides[id] = open;
  persistOpen();
  // Calm URL: toggling never rewrites the hash; only inbound #section links jump.
}

function jumpToSection(id: string): void {
  if (!sectionIds.value.includes(id)) return;
  if (!isSectionOpen(id)) onSectionToggle(id, true);
  void nextTick(() => {
    const el = document.getElementById(id);
    if (!el) return;
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    el.scrollIntoView?.({ behavior: reduce ? "auto" : "smooth", block: "start" });
    el.querySelector<HTMLElement>("summary")?.focus({ preventScroll: true });
  });
}

const PREFETCH_SLUGS = new Set([
  "weather",
  "calculator",
  "password-generator",
  "qr-generator",
  "url-shortener",
]);

function onPillIntent(tab: { id: string; to: Parameters<typeof prefetchRoute>[1] }): void {
  if (PREFETCH_SLUGS.has(tab.id)) prefetchRoute(router, tab.to);
}

function hashSectionId(hash: string | undefined): string {
  return (hash ?? "").replace(/^#/, "").slice(0, 32);
}

onMounted(() => {
  const id = hashSectionId(route.hash);
  if (id) jumpToSection(id);
});

/** External hash navigation (link click / back-forward) — toggles never write the hash. */
watch(
  () => route.hash,
  (hash) => {
    const id = hashSectionId(hash);
    if (id) jumpToSection(id);
  },
);

function toolRoute(tool: PlatformService): string {
  return resolveToolRoute(tool, can);
}

function sectionCount(section: ToolsPageSection): number {
  return section.services.length;
}

function tabPillClass(): string {
  return `${actionFamilyClass("1xx", false)} min-h-11`;
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
      class="mb-4 flex items-start gap-2 rounded-xl border border-transparent bg-surface-card px-3 py-2 text-sm text-surface-sage"
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
    <div v-else class="space-y-4">
      <ToolsCatalogSection
        v-if="showUtilsSection"
        id="utils"
        label="utils"
        :count="utilsSectionCount"
        :open="isSectionOpen('utils')"
        @toggle="onSectionToggle('utils', $event)"
      >
        <nav aria-label="utils tools">
          <ul class="flex list-none flex-wrap justify-start gap-2.5 p-0">
            <li v-for="tab in utilsTabs" :key="tab.id">
              <RouterLink
                :to="tab.to"
                :class="tabPillClass()"
                @mouseenter="onPillIntent(tab)"
                @focus="onPillIntent(tab)"
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
      </ToolsCatalogSection>
      <ToolsCatalogSection
        v-for="section in tileSections"
        :id="section.category"
        :key="section.category"
        :label="section.label"
        :count="sectionCount(section)"
        :open="isSectionOpen(section.category)"
        @toggle="onSectionToggle(section.category, $event)"
      >
        <ToolTileGrid
          presentation="public"
          :sections="[section]"
          :show-category-headings="false"
          :section-ids="false"
          :resolve-route="toolRoute"
          :tile-chip="toolsPageChipForSlug"
        />
      </ToolsCatalogSection>
    </div>
  </PageShell>
</template>
