<script setup lang="ts">
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import TaskList from "@/components/tasks/TaskList.vue";
import type { TaskItem, TaskStats } from "@/types";

defineProps<{
  tasks: TaskItem[];
  loading: boolean;
  filterStatus: string;
  total: number;
  page: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  stats?: TaskStats | null;
}>();

const emit = defineEmits<{
  select: [id: number];
  firstPage: [];
  prevPage: [];
  nextPage: [];
  lastPage: [];
  failedSyncs: [];
}>();
</script>

<template>
  <section
    id="tasks-tab-panel-queue"
    role="tabpanel"
    aria-labelledby="tasks-tab-tab-queue"
    tabindex="0"
    class="outline-none"
  >
    <TaskList
      :tasks="tasks"
      :loading="loading"
      :filter-status="filterStatus"
      @select="emit('select', $event)"
    />
    <AdminListFooter
      v-if="!loading"
      :total="total"
      :page="page"
      :total-pages="totalPages"
      :has-next-page="hasNextPage"
      :has-previous-page="hasPreviousPage"
      :loading="loading"
      :show-leading="Boolean(stats)"
      item-label="tasks"
      aria-label="tasks pagination"
      @first="emit('firstPage')"
      @prev="emit('prevPage')"
      @next="emit('nextPage')"
      @last="emit('lastPage')"
    >
      <template #leading>
        <div
          v-if="stats"
          class="flex flex-wrap items-center gap-2 text-xs text-surface-mid"
          aria-label="task stats"
        >
          <span>{{ stats.pending }} pending</span>
          <span class="text-surface-border">·</span>
          <span>{{ stats.completed }} completed</span>
          <span class="text-surface-border">·</span>
          <span>{{ stats.total }} total</span>
          <template v-if="stats.failed_syncs">
            <span class="text-surface-border">·</span>
            <button
              type="button"
              class="text-status-critical underline-offset-2 hover:underline"
              @click="emit('failedSyncs')"
            >
              {{ stats.failed_syncs }} failed syncs
            </button>
          </template>
        </div>
      </template>
    </AdminListFooter>
  </section>
</template>
