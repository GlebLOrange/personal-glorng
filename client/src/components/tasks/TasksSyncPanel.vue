<script setup lang="ts">
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import TaskSyncQueue from "@/components/tasks/TaskSyncQueue.vue";
import type { SyncQueueItem } from "@/types";

defineProps<{
  items: SyncQueueItem[];
  loading: boolean;
  canMutate: boolean;
  total: number;
  page: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}>();

const emit = defineEmits<{
  retry: [taskId: number];
  firstPage: [];
  prevPage: [];
  nextPage: [];
  lastPage: [];
}>();
</script>

<template>
  <section
    id="tasks-tab-panel-sync"
    role="tabpanel"
    aria-labelledby="tasks-tab-tab-sync"
    tabindex="0"
    class="outline-none"
  >
    <TaskSyncQueue
      :items="items"
      :loading="loading"
      :can-mutate="canMutate"
      @retry="emit('retry', $event)"
    />
    <AdminListFooter
      v-if="!loading"
      :total="total"
      :page="page"
      :total-pages="totalPages"
      :has-next-page="hasNextPage"
      :has-previous-page="hasPreviousPage"
      :loading="loading"
      item-label="items"
      ariaLabel="Task sync queue pagination"
      @first="emit('firstPage')"
      @prev="emit('prevPage')"
      @next="emit('nextPage')"
      @last="emit('lastPage')"
    />
  </section>
</template>
