<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from "vue";
import { useRoute, useRouter } from "vue-router";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import TaskCreateModal from "@/components/tasks/TaskCreateModal.vue";
import TaskDetailModal from "@/components/tasks/TaskDetailModal.vue";
import TaskIntakeList from "@/components/tasks/TaskIntakeList.vue";
import TaskList from "@/components/tasks/TaskList.vue";
import TaskSyncQueue from "@/components/tasks/TaskSyncQueue.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { statusBadgeClass } from "@/constants/filterColors";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { useTasks } from "@/composables/useTasks";

type Tab = "queue" | "intakes" | "sync";

const TASK_TABS: { id: Tab; label: string }[] = [
  { id: "queue", label: "queue" },
  { id: "intakes", label: "intakes" },
  { id: "sync", label: "sync" },
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
      <AdminTabBar
        panel-id-prefix="tasks-tab"
        :model-value="activeTab"
        :tabs="TASK_TABS"
        @update:model-value="switchTab"
      />

      <section
        v-if="activeTab === 'queue'"
        id="tasks-tab-panel-queue"
        role="tabpanel"
        aria-labelledby="tasks-tab-tab-queue"
        tabindex="0"
        class="outline-none"
      >
        <AdminListToolbar>
          <template #start>
            <div class="flex w-full min-w-0 flex-wrap items-center gap-3">
              <AdminFilterDropdown
                ref="filterDropdown"
                :has-active-filters="Boolean(filterStatus || searchQuery.trim())"
                :active-label="activeFilterLabel"
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
                    <BaseButton variant="ghost" size="sm" @click="onFailedSyncs">
                      open sync queue
                    </BaseButton>
                  </div>
                </template>
              </AdminFilterDropdown>
              <BaseInput
                v-model="searchQuery"
                type="search"
                class="min-w-0 flex-1"
                placeholder="search tasks"
                aria-label="search tasks"
              />
              <BaseButton
                v-if="isSuperuser"
                variant="primary"
                size="sm"
                class="ml-auto"
                :disabled="listLoading"
                @click="openCreate"
              >
                + task
              </BaseButton>
              <p v-else class="ml-auto text-xs text-surface-mid">
                View only — creating and status changes need superuser.
              </p>
            </div>
          </template>
        </AdminListToolbar>
        <TaskList
          :tasks="tasks"
          :loading="listLoading"
          :filter-status="filterStatus"
          @select="openDetail"
        />
        <AdminListFooter
          v-if="!listLoading"
          :total="total"
          :page="page"
          :total-pages="totalPages"
          :has-next-page="hasNextPage"
          :has-previous-page="hasPreviousPage"
          :loading="listLoading"
          item-label="tasks"
          ariaLabel="Tasks pagination"
          @first="goToPage(1)"
          @prev="goToPage(page - 1)"
          @next="goToPage(page + 1)"
          @last="goToPage(totalPages)"
        />
      </section>

      <section
        v-else-if="activeTab === 'intakes'"
        id="tasks-tab-panel-intakes"
        role="tabpanel"
        aria-labelledby="tasks-tab-tab-intakes"
        tabindex="0"
        class="outline-none"
      >
        <TaskIntakeList :intakes="intakes" :loading="intakesLoading" />
        <AdminListFooter
          v-if="!intakesLoading"
          :total="intakeTotal"
          :page="intakePage"
          :total-pages="intakeTotalPages"
          :has-next-page="hasNextIntakePage"
          :has-previous-page="hasPreviousIntakePage"
          :loading="intakesLoading"
          item-label="intakes"
          ariaLabel="Task intakes pagination"
          @first="goToIntakePage(1)"
          @prev="goToIntakePage(intakePage - 1)"
          @next="goToIntakePage(intakePage + 1)"
          @last="goToIntakePage(intakeTotalPages)"
        />
      </section>

      <section
        v-else-if="activeTab === 'sync'"
        id="tasks-tab-panel-sync"
        role="tabpanel"
        aria-labelledby="tasks-tab-tab-sync"
        tabindex="0"
        class="outline-none"
      >
        <TaskSyncQueue
          :items="syncQueue"
          :loading="syncLoading"
          :can-mutate="isSuperuser"
          @retry="retrySync"
        />
        <AdminListFooter
          v-if="!syncLoading"
          :total="syncTotal"
          :page="syncPage"
          :total-pages="syncTotalPages"
          :has-next-page="hasNextSyncPage"
          :has-previous-page="hasPreviousSyncPage"
          :loading="syncLoading"
          item-label="items"
          ariaLabel="Task sync queue pagination"
          @first="goToSyncPage(1)"
          @prev="goToSyncPage(syncPage - 1)"
          @next="goToSyncPage(syncPage + 1)"
          @last="goToSyncPage(syncTotalPages)"
        />
      </section>

      <TaskCreateModal
        v-if="isSuperuser"
        v-model:form="createForm"
        :open="showCreateForm"
        :saving="saving"
        @submit="createTask"
        @close="showCreateForm = false"
      />

      <TaskDetailModal
        v-if="selectedTask"
        :task="selectedTask"
        :loading="detailLoading"
        :can-mutate="isSuperuser"
        :status-updating="statusUpdating"
        @close="closeDetail"
        @retry-sync="retrySync"
        @update-status="updateTaskStatus(selectedTask.id, $event)"
      />
    </div>
  </AdminPageLayout>
</template>
