<script setup lang="ts">
import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import TaskCard from "@/components/tasks/TaskCard.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { ADMIN_SORT_HEADER_BUTTON_CLASS, ADMIN_TH_CLASS } from "@/constants/adminDataTable";
import type { TaskItem } from "@/types";

defineProps<{
  tasks: TaskItem[];
  loading: boolean;
  filterStatus: string;
  whenAriaSort: "ascending" | "descending" | "none";
  whenIndicator: string;
}>();

const emit = defineEmits<{ select: [id: number]; sortWhen: [] }>();

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
    <AdminDataTable table-label="tasks">
      <template #header>
        <th :class="ADMIN_TH_CLASS" scope="col">status</th>
        <th :class="ADMIN_TH_CLASS" scope="col" :aria-sort="whenAriaSort">
          <button
            type="button"
            :class="ADMIN_SORT_HEADER_BUTTON_CLASS"
            aria-label="sort by when"
            @click="emit('sortWhen')"
          >
            <ChevronIcon class-name="size-3 shrink-0" />
            when{{ whenIndicator }}
          </button>
        </th>
        <th :class="ADMIN_TH_CLASS" scope="col">title</th>
        <th :class="[ADMIN_TH_CLASS, 'w-px text-right']" scope="col">actions</th>
      </template>
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @select="emit('select', $event)"
      />
    </AdminDataTable>
  </div>
</template>
