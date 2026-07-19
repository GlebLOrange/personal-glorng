<script setup lang="ts">
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import TaskCard from "@/components/tasks/TaskCard.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import type { TaskItem } from "@/types";

defineProps<{
  tasks: TaskItem[];
  loading: boolean;
  filterStatus: string;
}>();

const emit = defineEmits<{ select: [id: number] }>();

const emptyMessage = (filterStatus: string): string => {
  if (filterStatus === "pending") return "No pending tasks.";
  if (filterStatus) return `No ${filterStatus.replaceAll("_", " ")} tasks.`;
  return "No tasks yet.";
};
</script>

<template>
  <AdminListSkeleton v-if="loading" label="Loading tasks" />

  <EmptyState v-else-if="tasks.length === 0" :description="emptyMessage(filterStatus)" />

  <div v-else class="space-y-1">
    <TaskCard v-for="task in tasks" :key="task.id" :task="task" @select="emit('select', $event)" />
  </div>
</template>
