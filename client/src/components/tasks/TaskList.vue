<script setup lang="ts">
import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import TaskCard from "@/components/tasks/TaskCard.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import {
  ADMIN_MOBILE_LIST_CLASS,
  ADMIN_TH_CLASS,
} from "@/constants/adminDataTable";
import type { TaskItem } from "@/types";

defineProps<{
  tasks: TaskItem[];
  loading: boolean;
  filterStatus: string;
}>();

const emit = defineEmits<{ select: [id: number] }>();

const emptyMessage = (filterStatus: string): string => {
  if (filterStatus === "pending") return "No pending tasks";
  if (filterStatus) return `No ${filterStatus.replaceAll("_", " ")} tasks`;
  return "No tasks yet";
};
</script>

<template>
  <AdminListSkeleton v-if="loading" label="Loading tasks" />

  <EmptyState v-else-if="tasks.length === 0" :description="emptyMessage(filterStatus)" />

  <div v-else class="min-w-0">
    <div :class="ADMIN_MOBILE_LIST_CLASS">
      <TaskCard
        v-for="task in tasks"
        :key="`m-${task.id}`"
        layout="card"
        :task="task"
        @select="emit('select', $event)"
      />
    </div>

    <AdminDataTable table-label="tasks">
      <template #header>
        <th :class="ADMIN_TH_CLASS">status</th>
        <th :class="ADMIN_TH_CLASS">when</th>
        <th :class="ADMIN_TH_CLASS">title</th>
        <th class="w-px px-2 text-right">
          <span class="sr-only">actions</span>
        </th>
      </template>
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        layout="table"
        :task="task"
        @select="emit('select', $event)"
      />
    </AdminDataTable>
  </div>
</template>
