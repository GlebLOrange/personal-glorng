<script setup lang="ts">
import AdminDataRow from "@/components/admin/AdminDataRow.vue";
import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import {
  ADMIN_MOBILE_LIST_CLASS,
  ADMIN_MOBILE_ROW_WRAP_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TD_TITLE_CLASS,
  ADMIN_TH_CLASS,
} from "@/constants/adminDataTable";
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
</script>

<template>
  <AdminPageLayout hub="admin" title="manage news sources" max-width="5xl" back-to="/admin">
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

      <template v-if="canWrite">
        <ToolbarPillButton
          action="create"
          class="ml-auto gap-1.5"
          :disabled="refreshing || loading"
          @click="refreshSources"
        >
          <RefreshIcon class-name="size-3.5" />
          {{ refreshButtonText }}
        </ToolbarPillButton>
        <ToolbarPillButton action="create" :disabled="loading" @click="openCreate">
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

        <div v-else class="mt-1 min-w-0">
          <div :class="ADMIN_MOBILE_LIST_CLASS">
            <div
              v-for="source in sources"
              :key="`m-${source.id}`"
              :class="[
                ADMIN_MOBILE_ROW_WRAP_CLASS,
                'flex min-w-0 items-center gap-2',
                canWrite ? 'cursor-pointer' : undefined,
              ]"
              :role="canWrite ? 'button' : undefined"
              :tabindex="canWrite ? 0 : undefined"
              @click="canWrite && openEditableSource(source)"
              @keydown.enter.prevent="canWrite && openEditableSource(source)"
              @keydown.space.prevent="canWrite && openEditableSource(source)"
            >
              <input
                v-if="canWrite"
                v-model="selectedSourceIds"
                type="checkbox"
                class="size-4 shrink-0 align-middle accent-accent-coral"
                :value="source.id"
                :disabled="refreshing || !source.enabled"
                :aria-label="`select ${source.name} for parser refresh`"
                @click.stop
                @keydown.stop
              />
              <StatusBadge
                :label="source.enabled ? 'enabled' : 'disabled'"
                :class-name="newsSourceEnabledClass(source.enabled)"
              />
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm text-surface-light" :title="source.name">
                  {{ source.name }}
                </p>
                <p
                  v-if="sourceMeta(source)"
                  class="mt-0.5 truncate text-xs text-surface-mid"
                  :title="sourceMeta(source)"
                >
                  {{ sourceMeta(source) }}
                </p>
              </div>
              <div class="flex shrink-0 items-center gap-0.5" @click.stop @keydown.stop>
                <span
                  v-if="source.last_error"
                  class="inline-flex text-status-warning"
                  :title="source.last_error"
                  aria-label="source has fetch error"
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
              </div>
            </div>
          </div>

          <AdminDataTable table-label="news sources">
            <template #header>
              <th v-if="canWrite" class="w-px px-3 py-1.5">
                <span class="sr-only">select</span>
              </th>
              <th :class="ADMIN_TH_CLASS">status</th>
              <th :class="ADMIN_TH_CLASS">name</th>
              <th :class="ADMIN_TH_CLASS">meta</th>
              <th class="w-px px-2 text-right">
                <span class="sr-only">actions</span>
              </th>
            </template>

            <AdminDataRow
              v-for="source in sources"
              :key="source.id"
              :interactive="canWrite"
              nested-interactive
              :col-span="canWrite ? 5 : 4"
              @click="openEditableSource(source)"
            >
              <td v-if="canWrite" :class="ADMIN_TD_CLASS" data-admin-row-stop @click.stop @keydown.stop>
                <input
                  v-model="selectedSourceIds"
                  type="checkbox"
                  class="size-4 shrink-0 align-middle accent-accent-coral"
                  :value="source.id"
                  :disabled="refreshing || !source.enabled"
                  :aria-label="`select ${source.name} for parser refresh`"
                />
              </td>
              <td :class="ADMIN_TD_CLASS">
                <StatusBadge
                  :label="source.enabled ? 'enabled' : 'disabled'"
                  :class-name="newsSourceEnabledClass(source.enabled)"
                />
              </td>
              <td :class="ADMIN_TD_TITLE_CLASS">
                <p class="truncate text-sm text-surface-light" :title="source.name">
                  {{ source.name }}
                </p>
              </td>
              <td :class="ADMIN_TD_MUTED_CLASS" :title="sourceMeta(source) || undefined">
                {{ sourceMeta(source) || "—" }}
              </td>
              <template #actions>
                <span
                  v-if="source.last_error"
                  class="inline-flex text-status-warning"
                  :title="source.last_error"
                  aria-label="source has fetch error"
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
            </AdminDataRow>
          </AdminDataTable>
        </div>

        <AdminListFooter
          :total="total"
          :page="page"
          :total-pages="totalPages"
          :has-next-page="hasNextPage"
          :has-previous-page="hasPreviousPage"
          :loading="loading"
          item-label="sources"
          aria-label="news sources pagination"
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
