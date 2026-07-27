<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import SyncIcon from "@/components/icons/SyncIcon.vue";
import TaskCreateModal from "@/components/tasks/TaskCreateModal.vue";
import TaskDetailModal from "@/components/tasks/TaskDetailModal.vue";
import TasksIntakesPanel from "@/components/tasks/TasksIntakesPanel.vue";
import TasksListPanel from "@/components/tasks/TasksListPanel.vue";
import TasksSyncPanel from "@/components/tasks/TasksSyncPanel.vue";
import SearchInput from "@/components/ui/SearchInput.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { statusBadgeClass } from "@/constants/filterColors";
import { effectiveSearchQuery } from "@/constants/search";
import { FILTER_MENU_ROW_CLASS } from "@/constants/toolbarPopover";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { useTasks } from "@/composables/useTasks";

type Tab = "queue" | "intakes" | "sync";

const TASK_TABS: { id: Tab; label: string; icon?: "sync" | "refresh" }[] = [
  { id: "queue", label: "queue" },
  { id: "intakes", label: "intakes" },
  { id: "sync", label: "sync", icon: "sync" },
];

const STATUS_FILTERS = [
  { label: "pending", value: "pending" },
  { label: "completed", value: "completed" },
  { label: "not completed", value: "not_completed" },
  { label: "postponed", value: "postponed" },
  { label: "cancelled", value: "cancelled" },
] as const;

const route = useRoute();
const router = useRouter();
const activeTab = ref<Tab>("queue");
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");

const { isSuperuser } = usePermissions();

const {
  tasks,
  syncQueue,
  intakes,
  selectedTask,
  filterStatus,
  searchQuery,
  page,
  showCreateForm,
  createForm,
  listLoading,
  intakesLoading,
  syncLoading,
  detailLoading,
  saving,
  statusUpdating,
  hasNextPage,
  hasPreviousPage,
  hasNextIntakePage,
  hasPreviousIntakePage,
  hasNextSyncPage,
  hasPreviousSyncPage,
  intakePage,
  syncPage,
  totalPages,
  intakeTotalPages,
  syncTotalPages,
  total,
  intakeTotal,
  syncTotal,
  loadTasks,
  loadIntakes,
  loadSyncQueue,
  openDetail,
  closeDetail,
  retrySync,
  updateTaskStatus,
  openCreate,
  createTask,
  goToPage,
  goToIntakePage,
  goToSyncPage,
} = useTasks();

const activeFilterLabel = computed(
  () => STATUS_FILTERS.find((chip) => chip.value === filterStatus.value)?.label,
);

function parseTaskTab(value: unknown): Tab | null {
  return typeof value === "string" && TASK_TABS.some((item) => item.id === value)
    ? (value as Tab)
    : null;
}

function switchTab(tab: string): void {
  if (!TASK_TABS.some((item) => item.id === tab)) return;
  activeTab.value = tab as Tab;
  void router.replace({ query: { ...route.query, tab } });
  if (tab === "intakes") void loadIntakes();
  if (tab === "sync") void loadSyncQueue();
}

function setStatusFilter(status: string): void {
  filterStatus.value = status;
  filterDropdownRef.value?.close();
}

function clearFilters(): void {
  filterStatus.value = "";
  searchQuery.value = "";
  filterDropdownRef.value?.close();
}

function onFailedSyncs(): void {
  filterDropdownRef.value?.close();
  switchTab("sync");
}

watch(activeTab, (tab) => {
  if (tab !== "queue") filterDropdownRef.value?.close();
});

useScrollListFingerprint(
  () =>
    `${activeTab.value}:${filterStatus.value}:${searchQuery.value}:${page.value}:${tasks.value[0]?.id ?? ""}:${intakes.value[0]?.id ?? ""}:${syncQueue.value[0]?.id ?? ""}`,
);

onMounted(() => {
  const tab = parseTaskTab(route.query.tab);
  if (tab) {
    activeTab.value = tab;
    if (tab === "intakes") void loadIntakes();
    if (tab === "sync") void loadSyncQueue();
  }
  void loadTasks();
});
</script>

<template>
  <AdminPageLayout hub="tools" title="tasks" max-width="xl">
    <div class="min-w-0">
      <div class="mb-3 space-y-2">
        <div class="flex min-w-0 flex-wrap items-center gap-2">
          <AdminFilterDropdown
            v-show="activeTab === 'queue'"
            ref="filterDropdown"
            :has-active-filters="Boolean(filterStatus || effectiveSearchQuery(searchQuery))"
            :active-label="activeFilterLabel"
            :option-labels="STATUS_FILTERS.map((chip) => chip.label)"
            @clear="clearFilters"
          >
            <template #chips>
              <AdminFilterChip
                v-for="chip in STATUS_FILTERS"
                :key="chip.value"
                :label="chip.label"
                :active="filterStatus === chip.value"
                :color-class="statusBadgeClass(chip.value)"
                @click="setStatusFilter(chip.value)"
              />
            </template>
            <template #footer>
              <div class="mt-3 border-t border-surface-border pt-3">
                <button
                  type="button"
                  :class="[
                    FILTER_MENU_ROW_CLASS,
                    'justify-start border-transparent bg-transparent text-accent-violet hover:enabled:bg-accent-violet/15 focus-visible:ring-accent-violet/50',
                  ]"
                  @click="onFailedSyncs"
                >
                  <SyncIcon class-name="size-3.5 shrink-0" />
                  open sync queue
                </button>
              </div>
            </template>
          </AdminFilterDropdown>

          <AdminTabBar
            flush
            panel-id-prefix="tasks-tab"
            :model-value="activeTab"
            :tabs="TASK_TABS"
            @update:model-value="switchTab"
          />

          <ToolbarPillButton
            v-if="isSuperuser"
            v-show="activeTab === 'queue'"
            family="2xx"
            class="ml-auto"
            :disabled="listLoading"
            @click="openCreate"
          >
            + task
          </ToolbarPillButton>
        </div>

        <template v-if="activeTab === 'queue'">
          <SearchInput v-model="searchQuery" class="w-full" placeholder="search tasks" />
          <p v-if="!isSuperuser" class="text-xs text-surface-mid">
            View only — creating and status changes need superuser.
          </p>
        </template>
      </div>

      <TasksListPanel
        v-if="activeTab === 'queue'"
        :tasks="tasks"
        :loading="listLoading"
        :filter-status="filterStatus"
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        @select="openDetail"
        @first-page="goToPage(1)"
        @prev-page="goToPage(page - 1)"
        @next-page="goToPage(page + 1)"
        @last-page="goToPage(totalPages)"
      />

      <TasksIntakesPanel
        v-else-if="activeTab === 'intakes'"
        :intakes="intakes"
        :loading="intakesLoading"
        :total="intakeTotal"
        :page="intakePage"
        :total-pages="intakeTotalPages"
        :has-next-page="hasNextIntakePage"
        :has-previous-page="hasPreviousIntakePage"
        @first-page="goToIntakePage(1)"
        @prev-page="goToIntakePage(intakePage - 1)"
        @next-page="goToIntakePage(intakePage + 1)"
        @last-page="goToIntakePage(intakeTotalPages)"
      />

      <TasksSyncPanel
        v-else-if="activeTab === 'sync'"
        :items="syncQueue"
        :loading="syncLoading"
        :can-mutate="isSuperuser"
        :total="syncTotal"
        :page="syncPage"
        :total-pages="syncTotalPages"
        :has-next-page="hasNextSyncPage"
        :has-previous-page="hasPreviousSyncPage"
        @retry="retrySync"
        @first-page="goToSyncPage(1)"
        @prev-page="goToSyncPage(syncPage - 1)"
        @next-page="goToSyncPage(syncPage + 1)"
        @last-page="goToSyncPage(syncTotalPages)"
      />

      <TaskCreateModal
        v-if="isSuperuser"
        v-model:form="createForm"
        :open="showCreateForm"
        :saving="saving"
        @submit="createTask"
        @close="showCreateForm = false"
      />

      <TaskDetailModal
        :open="selectedTask !== null"
        :task="selectedTask"
        :loading="detailLoading"
        :can-mutate="isSuperuser"
        :status-updating="statusUpdating"
        @close="closeDetail"
        @retry-sync="retrySync"
        @update-status="selectedTask && updateTaskStatus(selectedTask.id, $event)"
      />
    </div>
  </AdminPageLayout>
</template>
