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

function intakeText(item: TaskIntakeItem): string {
  return item.inbound_text?.trim() || `Intake #${item.id}`;
}
</script>

<template>
  <AdminListSkeleton v-if="loading" label="Loading task intakes" />

  <EmptyState v-else-if="intakes.length === 0" description="no task intakes yet" />

  <div v-else class="min-w-0">
    <AdminDataTable table-label="task intakes">
      <template #header>
        <th :class="ADMIN_TH_CLASS" scope="col">status</th>
        <th :class="ADMIN_TH_CLASS" scope="col">text</th>
        <th :class="ADMIN_TH_CLASS" scope="col">intake id</th>
        <th :class="ADMIN_TH_CLASS" scope="col">task</th>
        <th :class="ADMIN_TH_CLASS" scope="col">created</th>
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
        <th :class="ADMIN_TH_ROW_CLASS" scope="row">
          <span class="line-clamp-1" :title="intakeText(item)">{{ intakeText(item) }}</span>
        </th>
        <td :class="ADMIN_TD_MUTED_CLASS">#{{ item.id }}</td>
        <td :class="ADMIN_TD_MUTED_CLASS">
          {{ item.task_id ? `#${item.task_id}` : "—" }}
        </td>
        <td :class="ADMIN_TD_MUTED_CLASS">{{ formatDate(item.created_at) }}</td>
      </tr>
    </AdminDataTable>
  </div>

  <TaskIntakeDetailDrawer :open="drawerOpen" :intake="selectedIntake" @close="closeDrawer" />
</template>
