<script setup lang="ts">
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import TaskList from "@/components/tasks/TaskList.vue";
import type { TaskItem } from "@/types";

defineProps<{
  tasks: TaskItem[];
  loading: boolean;
  filterStatus: string;
  total: number;
  page: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}>();

const emit = defineEmits<{
  select: [id: number];
  firstPage: [];
  prevPage: [];
  nextPage: [];
  lastPage: [];
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
      item-label="tasks"
      aria-label="tasks pagination"
      @first="emit('firstPage')"
      @prev="emit('prevPage')"
      @next="emit('nextPage')"
      @last="emit('lastPage')"
    />
  </section>
</template>
