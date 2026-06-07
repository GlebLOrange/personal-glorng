<script setup lang="ts">
import TaskCard from "@/components/tasks/TaskCard.vue";
import type { TaskItem } from "@/types";

defineProps<{
  tasks: TaskItem[];
  loading: boolean;
  filterStatus: string;
}>();

const emit = defineEmits<{ select: [id: number] }>();

const skeletonRows = 5;

const emptyMessage = (filterStatus: string): string => {
  if (filterStatus === "pending") return "No pending tasks.";
  if (filterStatus) return `No ${filterStatus.replaceAll("_", " ")} tasks on this page.`;
  return "No tasks on this page.";
};
</script>

<template>
  <div v-if="loading" class="flex flex-col gap-3">
    <div
      v-for="n in skeletonRows"
      :key="n"
      class="rounded-lg border border-surface-border bg-surface-card p-4 animate-pulse"
    >
      <div class="h-3 w-24 bg-surface-border rounded mb-2" />
      <div class="h-4 w-48 bg-surface-border rounded mb-3" />
      <div class="h-3 w-32 bg-surface-border rounded" />
    </div>
  </div>

  <div v-else-if="tasks.length === 0" class="text-surface-mid text-sm text-center py-8">
    {{ emptyMessage(filterStatus) }}
  </div>

  <div v-else class="flex flex-col gap-3">
    <TaskCard v-for="task in tasks" :key="task.id" :task="task" @select="emit('select', $event)" />
  </div>
</template>
