<script setup lang="ts">
import { onMounted, ref } from "vue";

import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import TaskCreateModal from "@/components/tasks/TaskCreateModal.vue";
import TaskDetailDrawer from "@/components/tasks/TaskDetailDrawer.vue";
import TaskFilters from "@/components/tasks/TaskFilters.vue";
import TaskIntakeList from "@/components/tasks/TaskIntakeList.vue";
import TaskList from "@/components/tasks/TaskList.vue";
import TaskPagination from "@/components/tasks/TaskPagination.vue";
import TaskSummaryBar from "@/components/tasks/TaskSummaryBar.vue";
import TaskSyncQueue from "@/components/tasks/TaskSyncQueue.vue";
import { useTasks } from "@/composables/useTasks";

type Tab = "queue" | "intakes" | "sync";

const TASK_TABS: { id: Tab; label: string }[] = [
  { id: "queue", label: "queue" },
  { id: "intakes", label: "intakes" },
  { id: "sync", label: "sync" },
];

const activeTab = ref<Tab>("queue");

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
  hasNextPage,
  taskCountLabel,
  loadTasks,
  loadStats,
  loadIntakes,
  loadSyncQueue,
  openDetail,
  closeDetail,
  retrySync,
  openCreate,
  createTask,
  goToPage,
} = useTasks();

function switchTab(tab: string): void {
  if (!TASK_TABS.some((item) => item.id === tab)) return;
  activeTab.value = tab as Tab;
  if (tab === "intakes") void loadIntakes();
  if (tab === "sync") void loadSyncQueue();
}

onMounted(() => {
  void loadTasks();
  void loadStats();
});
</script>

<template>
  <AdminPageLayout title="tasks" max-width="xl">
    <TaskSummaryBar :stats="stats" :loading="statsLoading" />

    <AdminTabBar :model-value="activeTab" :tabs="TASK_TABS" @update:model-value="switchTab" />

    <div v-if="activeTab === 'queue'">
      <TaskFilters
        v-model:filter-status="filterStatus"
        :task-count-label="taskCountLabel"
        @create="openCreate"
      />
      <TaskList
        :tasks="tasks"
        :loading="listLoading"
        :filter-status="filterStatus"
        @select="openDetail"
      />
      <TaskPagination
        :page="page"
        :has-next-page="hasNextPage"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
      />
    </div>

    <TaskIntakeList
      v-else-if="activeTab === 'intakes'"
      :intakes="intakes"
      :loading="intakesLoading"
    />

    <TaskSyncQueue
      v-else-if="activeTab === 'sync'"
      :items="syncQueue"
      :loading="syncLoading"
      @retry="retrySync"
    />

    <TaskCreateModal
      v-model:form="createForm"
      :open="showCreateForm"
      :saving="saving"
      @submit="createTask"
      @close="showCreateForm = false"
    />

    <TaskDetailDrawer
      v-if="selectedTask"
      :task="selectedTask"
      :loading="detailLoading"
      @close="closeDetail"
      @retry-sync="retrySync"
    />
  </AdminPageLayout>
</template>
