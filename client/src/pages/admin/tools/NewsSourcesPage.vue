<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminTabBar, { type AdminTab } from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import NewsSourceDrawer from "@/components/news/NewsSourceDrawer.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";
import { newsSourceEnabledClass } from "@/constants/filterColors";
import { ENABLED_FILTERS, useNewsSources } from "@/composables/useNewsSources";
import { usePermissions } from "@/composables/usePermissions";

const router = useRouter();
const { can } = usePermissions();

const {
  sources,
  page,
  enabledFilter,
  total,
  totalPages,
  selectedSourceIds,
  form,
  drawerOpen,
  drawerMode,
  loading,
  saving,
  refreshing,
  deletingId,
  canWrite,
  loadError,
  refreshButtonText,
  hasNextPage,
  hasPreviousPage,
  hasActiveFilters,
  activeFilterLabel,
  emptyFilterDescription,
  setEnabledFilter,
  clearFilters,
  sourceMeta,
  loadSources,
  goToPage,
  openCreate,
  openEditableSource,
  closeDrawer,
  updateForm,
  saveSource,
  refreshSources,
  deleteSource,
} = useNewsSources();

const surfaceTabs = computed((): AdminTab[] => {
  const items: AdminTab[] = [{ id: "digest", label: "digest", family: "1xx" }];
  if (can("news", "read")) {
    items.push({ id: "manage", label: "manage", family: "1xx" });
  }
  return items;
});

/** Neither digest nor manage is selected while on this page. */
const surfaceTab = computed({
  get: () => "sources",
  set: (id: string) => {
    void onSurfaceTab(id);
  },
});

async function onSurfaceTab(id: string): Promise<void> {
  if (id === "manage") {
    await router.push({ name: "news", query: { manage: "1" } });
    return;
  }
  await router.push({ name: "news", query: {} });
}
</script>

<template>
  <AdminPageLayout hub="tools" title="news sources" max-width="xl" back-to="/news">
    <div class="mb-3 flex min-w-0 flex-wrap items-center gap-2">
      <AdminFilterDropdown
        ref="filterDropdown"
        :has-active-filters="hasActiveFilters"
        :active-label="activeFilterLabel"
        @clear="clearFilters"
      >
        <template #chips>
          <AdminFilterChip
            v-for="chip in ENABLED_FILTERS"
            :key="chip.value"
            :label="chip.label"
            :active="enabledFilter === chip.value"
            :color-class="newsSourceEnabledClass(chip.value === 'enabled')"
            :disabled="loading"
            @click="setEnabledFilter(chip.value)"
          />
        </template>
      </AdminFilterDropdown>

      <AdminTabBar
        v-if="surfaceTabs.length > 0"
        v-model="surfaceTab"
        flush
        panel-id-prefix="news-sources-surface"
        :tabs="surfaceTabs"
      />

      <template v-if="canWrite">
        <ToolbarPillButton
          family="3xx"
          class="ml-auto"
          :disabled="refreshing || loading"
          @click="refreshSources"
        >
          {{ refreshButtonText }}
        </ToolbarPillButton>
        <ToolbarPillButton family="1xx" :disabled="loading" @click="openCreate">
          + source
        </ToolbarPillButton>
      </template>
    </div>

    <div class="min-w-0 divide-y divide-surface-border/40">
      <AdminListSkeleton v-if="loading" label="Loading sources" />

      <Card v-else-if="loadError" role="alert">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-sm text-status-yellow">News sources could not be loaded.</p>
          <BaseButton variant="ghost" size="sm" @click="loadSources">retry</BaseButton>
        </div>
      </Card>

      <template v-else>
        <EmptyState v-if="sources.length === 0" :description="emptyFilterDescription" />

        <template v-else>
          <AdminListRow
            v-for="source in sources"
            :key="source.id"
            :interactive="canWrite"
            :nested-interactive="canWrite"
            reveal-actions-on-hover
            @click="openEditableSource(source)"
          >
            <template #leading>
              <input
                v-if="canWrite"
                v-model="selectedSourceIds"
                type="checkbox"
                class="size-4 accent-accent-blue"
                :value="source.id"
                :disabled="refreshing || !source.enabled"
                :aria-label="`Select ${source.name} for parser refresh`"
                @click.stop
                @keydown.stop
              />
            </template>
            <template #badge>
              <StatusBadge
                :label="source.enabled ? 'enabled' : 'disabled'"
                :class-name="newsSourceEnabledClass(source.enabled)"
              />
            </template>
            <template #primary>
              <span :title="source.name">{{ source.name }}</span>
            </template>
            <template v-if="source.last_fetched_at" #meta>
              <span>{{ sourceMeta(source) }}</span>
            </template>
            <template #actions>
              <span
                v-if="source.last_error"
                class="text-xs text-status-yellow"
                :title="source.last_error"
                aria-label="Source has fetch error"
              >
                ⚠
              </span>
              <IconEditButton
                v-if="canWrite"
                aria-label="edit source"
                @click="openEditableSource(source)"
              />
              <IconCloseButton
                v-if="canWrite"
                aria-label="Delete source"
                :disabled="deletingId === source.id"
                @click="deleteSource(source, $event)"
              />
            </template>
          </AdminListRow>
        </template>

        <AdminListFooter
          :total="total"
          :page="page"
          :total-pages="totalPages"
          :has-next-page="hasNextPage"
          :has-previous-page="hasPreviousPage"
          :loading="loading"
          item-label="sources"
          ariaLabel="News sources pagination"
          @first="goToPage(1)"
          @prev="goToPage(page - 1)"
          @next="goToPage(page + 1)"
          @last="goToPage(totalPages)"
        />
      </template>
    </div>

    <NewsSourceDrawer
      v-if="canWrite"
      :open="drawerOpen"
      :mode="drawerMode"
      :form="form"
      :loading="saving"
      @update:form="updateForm"
      @close="closeDrawer"
      @save="saveSource"
    />
  </AdminPageLayout>
</template>
