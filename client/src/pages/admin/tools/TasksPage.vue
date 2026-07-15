<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import TaskCreateModal from "@/components/tasks/TaskCreateModal.vue";
import TaskDetailModal from "@/components/tasks/TaskDetailModal.vue";
import TaskFilters from "@/components/tasks/TaskFilters.vue";
import TaskIntakeList from "@/components/tasks/TaskIntakeList.vue";
import TaskList from "@/components/tasks/TaskList.vue";
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
  total,
  intakeTotal,
  syncTotal,
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
      <TaskSummaryBar
        v-model:filter-status="filterStatus"
        :stats="stats"
        :loading="statsLoading"
        @switch-tab="switchTab"
      >
        <template #actions>
          <TaskFilters :can-mutate="isSuperuser" @create="openCreate" />
        </template>
      </TaskSummaryBar>

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
        <div v-if="!listLoading && tasks.length > 0" class="mb-1">
          <AdminListToolbar
            :total="total"
            :page="page"
            :total-pages="totalPages"
            :has-next-page="hasNextPage"
            :has-previous-page="hasPreviousPage"
            :loading="listLoading"
            item-label="tasks"
            ariaLabel="Tasks pagination"
            @prev="goToPage(page - 1)"
            @next="goToPage(page + 1)"
          />
        </div>
        <TaskList
          :tasks="tasks"
          :loading="listLoading"
          :filter-status="filterStatus"
          @select="openDetail"
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
        <div v-if="!intakesLoading && intakes.length > 0" class="mb-1">
          <AdminListToolbar
            :total="intakeTotal"
            :page="intakePage"
            :total-pages="intakeTotalPages"
            :has-next-page="hasNextIntakePage"
            :has-previous-page="hasPreviousIntakePage"
            :loading="intakesLoading"
            item-label="intakes"
            ariaLabel="Task intakes pagination"
            @prev="goToIntakePage(intakePage - 1)"
            @next="goToIntakePage(intakePage + 1)"
          />
        </div>
        <TaskIntakeList :intakes="intakes" :loading="intakesLoading" />
      </section>

      <section
        v-else-if="activeTab === 'sync'"
        id="tasks-tab-panel-sync"
        role="tabpanel"
        aria-labelledby="tasks-tab-tab-sync"
        tabindex="0"
        class="outline-none"
      >
        <div v-if="!syncLoading && syncQueue.length > 0" class="mb-1">
          <AdminListToolbar
            :total="syncTotal"
            :page="syncPage"
            :total-pages="syncTotalPages"
            :has-next-page="hasNextSyncPage"
            :has-previous-page="hasPreviousSyncPage"
            :loading="syncLoading"
            item-label="items"
            ariaLabel="Task sync queue pagination"
            @prev="goToSyncPage(syncPage - 1)"
            @next="goToSyncPage(syncPage + 1)"
          />
        </div>
        <TaskSyncQueue
          :items="syncQueue"
          :loading="syncLoading"
          :can-mutate="isSuperuser"
          @retry="retrySync"
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
