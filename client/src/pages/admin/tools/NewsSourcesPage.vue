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
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import StatusIcon from "@/components/icons/StatusIcon.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
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
  showDeleteConfirm,
  deleteConfirmMessage,
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
  requestDeleteSource,
  confirmDeleteSource,
  cancelDeleteSource,
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
        :option-labels="ENABLED_FILTERS.map((chip) => chip.label)"
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
          family="5xx"
          class="ml-auto gap-1.5"
          :disabled="refreshing || loading"
          @click="refreshSources"
        >
          <RefreshIcon class-name="size-3.5" />
          {{ refreshButtonText }}
        </ToolbarPillButton>
        <ToolbarPillButton family="2xx" :disabled="loading" @click="openCreate">
          + source
        </ToolbarPillButton>
      </template>
    </div>

    <div class="min-w-0">
      <AdminListSkeleton v-if="loading" label="Loading sources" />

      <ErrorState
        v-else-if="loadError"
        message="News sources could not be loaded."
        show-retry
        @retry="loadSources"
      />

      <template v-else>
        <EmptyState v-if="sources.length === 0" :description="emptyFilterDescription" />

        <div v-else class="min-w-0">
          <AdminListRow
            v-for="source in sources"
            :key="source.id"
            :interactive="canWrite"
            :nested-interactive="canWrite"
            reveal-actions-on-hover
            :status-class="newsSourceEnabledClass(source.enabled)"
            @click="openEditableSource(source)"
          >
            <template #leading>
              <input
                v-if="canWrite"
                v-model="selectedSourceIds"
                type="checkbox"
                class="size-4 shrink-0 align-middle accent-accent-blue"
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
                class="inline-flex text-status-warning"
                :title="source.last_error"
                aria-label="Source has fetch error"
              >
                <StatusIcon status="warning" class-name="size-4" />
              </span>
              <IconEditButton
                v-if="canWrite"
                aria-label="edit source"
                @click="openEditableSource(source)"
              />
              <IconCloseButton
                v-if="canWrite"
                aria-label="delete source"
                :disabled="deletingId === source.id"
                @click="requestDeleteSource(source, $event)"
              />
            </template>
          </AdminListRow>
        </div>

        <AdminListFooter
          :total="total"
          :page="page"
          :total-pages="totalPages"
          :has-next-page="hasNextPage"
          :has-previous-page="hasPreviousPage"
          :loading="loading"
          item-label="sources"
          aria-label="News sources pagination"
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

    <ConfirmDialog
      v-if="canWrite"
      :open="showDeleteConfirm"
      title="delete source"
      :message="deleteConfirmMessage"
      confirm-label="delete"
      loading-label="deleting…"
      :loading="deletingId !== null"
      danger
      @confirm="confirmDeleteSource"
      @cancel="cancelDeleteSource"
    />
  </AdminPageLayout>
</template>
