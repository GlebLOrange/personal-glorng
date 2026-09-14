<script setup lang="ts">
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import SyncIcon from "@/components/icons/SyncIcon.vue";
import TaskSyncQueue from "@/components/tasks/TaskSyncQueue.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
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
  processing?: boolean;
}>();

const emit = defineEmits<{
  retry: [taskId: number];
  syncNow: [];
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
    <div
      v-if="canMutate"
      class="mb-3 flex justify-end"
    >
      <BaseButton
        variant="ghost"
        size="sm"
        class="gap-1.5"
        :disabled="loading || processing"
        aria-label="process sync queue now"
        @click="emit('syncNow')"
      >
        <SyncIcon class-name="size-3.5" />
        Sync now
      </BaseButton>
    </div>
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
      aria-label="task sync queue pagination"
      @first="emit('firstPage')"
      @prev="emit('prevPage')"
      @next="emit('nextPage')"
      @last="emit('lastPage')"
    />
  </section>
</template>
