<script setup lang="ts">
import { ref } from "vue";

import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import TaskIntakeDetailDrawer from "@/components/tasks/TaskIntakeDetailDrawer.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { statusBadgeClass, statusLabel } from "@/constants/taskStatus";
import { formatDate } from "@/utils/format";
import type { TaskIntakeItem } from "@/types";

defineProps<{
  intakes: TaskIntakeItem[];
  loading: boolean;
}>();

const selectedIntake = ref<TaskIntakeItem | null>(null);
const drawerOpen = ref(false);

function openIntake(item: TaskIntakeItem): void {
  selectedIntake.value = item;
  drawerOpen.value = true;
}

function closeDrawer(): void {
  drawerOpen.value = false;
  selectedIntake.value = null;
}
</script>

<template>
  <AdminListSkeleton v-if="loading" label="Loading task intakes" />

  <EmptyState v-else-if="intakes.length === 0" description="No task intakes yet." />

  <div v-else class="space-y-1">
    <AdminListRow
      v-for="item in intakes"
      :key="item.id"
      interactive
      @click="openIntake(item)"
    >
      <template #badge>
        <StatusBadge
          :label="statusLabel(item.status)"
          :class-name="statusBadgeClass(item.status)"
        />
      </template>
      <template #primary>
        <span class="line-clamp-1" :title="item.inbound_text || undefined">
          {{ item.inbound_text?.trim() || `Intake #${item.id}` }}
        </span>
      </template>
      <template #meta>
        <span>Intake #{{ item.id }}</span>
        <span v-if="item.task_id"> · → Task #{{ item.task_id }}</span>
      </template>
      <template #time>{{ formatDate(item.created_at) }}</template>
    </AdminListRow>
  </div>

  <TaskIntakeDetailDrawer :open="drawerOpen" :intake="selectedIntake" @close="closeDrawer" />
</template>
