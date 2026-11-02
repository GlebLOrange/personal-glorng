<script setup lang="ts">
import { ref } from "vue";

import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import TaskIntakeDetailDrawer from "@/components/tasks/TaskIntakeDetailDrawer.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import {
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TH_CLASS,
  ADMIN_TH_ROW_CLASS,
  ADMIN_TR_CLASS,
} from "@/constants/adminDataTable";
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

function intakeInfo(item: TaskIntakeItem): string {
  const title = item.draft_json?.title;
  if (typeof title === "string" && title.trim()) return title.trim();
  return item.inbound_text?.trim() || `Intake #${item.id}`;
}

function intakeTask(item: TaskIntakeItem): string | null {
  return item.task_id ? `#${item.task_id}` : null;
}

function intakeUpdated(item: TaskIntakeItem): string {
  return formatDate(item.updated_at ?? item.created_at);
}
</script>

<template>
  <AdminListSkeleton v-if="loading" label="Loading task intakes" />

  <EmptyState v-else-if="intakes.length === 0" description="no task intakes yet" />

  <div v-else class="min-w-0">
    <AdminDataTable table-label="task intakes">
      <template #header>
        <th :class="ADMIN_TH_CLASS" scope="col">status</th>
        <th :class="ADMIN_TH_CLASS" scope="col">task</th>
        <th :class="ADMIN_TH_CLASS" scope="col">info</th>
        <th :class="ADMIN_TH_CLASS" scope="col">updated</th>
      </template>
      <tr
        v-for="item in intakes"
        :key="item.id"
        :class="[ADMIN_TR_CLASS, 'cursor-pointer']"
        role="button"
        tabindex="0"
        @click="openIntake(item)"
        @keydown.enter.prevent="openIntake(item)"
        @keydown.space.prevent="openIntake(item)"
      >
        <td :class="ADMIN_TD_CLASS">
          <StatusBadge
            :label="statusLabel(item.status)"
            :class-name="statusBadgeClass(item.status)"
          />
        </td>
        <td :class="ADMIN_TD_MUTED_CLASS">
          <span v-if="intakeTask(item)">{{ intakeTask(item) }}</span>
          <span v-else class="text-muted" aria-label="no linked task">—</span>
        </td>
        <th :class="ADMIN_TH_ROW_CLASS" scope="row">
          <span class="line-clamp-1" :title="intakeInfo(item)">{{ intakeInfo(item) }}</span>
        </th>
        <td :class="ADMIN_TD_MUTED_CLASS">{{ intakeUpdated(item) }}</td>
      </tr>
    </AdminDataTable>
  </div>

  <TaskIntakeDetailDrawer :open="drawerOpen" :intake="selectedIntake" @close="closeDrawer" />
</template>
