<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import TaskCreateModal from "@/components/tasks/TaskCreateModal.vue";
import TaskDetailModal from "@/components/tasks/TaskDetailModal.vue";
import TaskFilters from "@/components/tasks/TaskFilters.vue";
import TaskIntakeList from "@/components/tasks/TaskIntakeList.vue";
import TaskList from "@/components/tasks/TaskList.vue";
import BasePagination from "@/components/ui/BasePagination.vue";
import TaskSummaryBar from "@/components/tasks/TaskSummaryBar.vue";
import TaskSyncQueue from "@/components/tasks/TaskSyncQueue.vue";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { useTasks } from "@/composables/useTasks";

type Tab = "queue" | "intakes" | "sync";

const TASK_TABS: { id: Tab; label: string }[] = [
  { id: "queue", label: "queue" },
  { id: "intakes", label: "intakes" },
  { id: "sync", label: "sync" },
];

const route = useRoute();
const router = useRouter();
const activeTab = ref<Tab>("queue");

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

const { isSuperuser } = usePermissions();

const {
  tasks,
  stats,
  syncQueue,
  intakes,
  selectedTask,
  filterStatus,
  page,
  showCreateForm,
  createForm,
  listLoading,
  statsLoading,
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
  taskCountLabel,
  loadTasks,
  loadStats,
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

useScrollListFingerprint(
  () =>
    `${activeTab.value}:${filterStatus.value}:${page.value}:${tasks.value[0]?.id ?? ""}:${intakes.value[0]?.id ?? ""}:${syncQueue.value[0]?.id ?? ""}`,
);

onMounted(() => {
  const tab = parseTaskTab(route.query.tab);
  if (tab) {
    activeTab.value = tab;
    if (tab === "intakes") void loadIntakes();
    if (tab === "sync") void loadSyncQueue();
  }
  void loadTasks();
  void loadStats();
});
</script>

<template>
  <AdminPageLayout title="tasks" max-width="xl">
    <div class="min-w-0">
    <TaskSummaryBar :stats="stats" :loading="statsLoading" />

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
      <TaskFilters
        v-model:filter-status="filterStatus"
        :task-count-label="taskCountLabel"
        :can-mutate="isSuperuser"
        @create="openCreate"
      />
      <TaskList
        :tasks="tasks"
        :loading="listLoading"
        :filter-status="filterStatus"
        @select="openDetail"
      />
      <BasePagination
        v-if="totalPages > 1"
        class="pt-4"
        aria-label="Tasks pagination"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
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
      <TaskIntakeList
        :intakes="intakes"
        :loading="intakesLoading"
      />
      <BasePagination
        v-if="intakeTotalPages > 1"
        class="pt-4"
        aria-label="Task intakes pagination"
        :page="intakePage"
        :total-pages="intakeTotalPages"
        :has-next-page="hasNextIntakePage"
        :has-previous-page="hasPreviousIntakePage"
        @prev="goToIntakePage(intakePage - 1)"
        @next="goToIntakePage(intakePage + 1)"
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
      <BasePagination
        v-if="syncTotalPages > 1"
        class="pt-4"
        aria-label="Task sync queue pagination"
        :page="syncPage"
        :total-pages="syncTotalPages"
        :has-next-page="hasNextSyncPage"
        :has-previous-page="hasPreviousSyncPage"
        @prev="goToSyncPage(syncPage - 1)"
        @next="goToSyncPage(syncPage + 1)"
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
