<script setup lang="ts">
import { ref } from "vue";

import AdminDataRow from "@/components/admin/AdminDataRow.vue";
import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import SyncIcon from "@/components/icons/SyncIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import {
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TH_CLASS,
  ADMIN_TH_ROW_CLASS,
} from "@/constants/adminDataTable";
import { statusBadgeClass, statusLabel } from "@/constants/taskStatus";
import { formatDate } from "@/utils/format";
import type { SyncQueueItem } from "@/types";

defineProps<{
  items: SyncQueueItem[];
  loading: boolean;
  canMutate?: boolean;
}>();

const emit = defineEmits<{ retry: [taskId: number] }>();

const expandedIds = ref<Set<number>>(new Set());

function toggleExpanded(id: number): void {
  const next = new Set(expandedIds.value);
  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }
  expandedIds.value = next;
}

function syncPrimary(item: SyncQueueItem): string {
  return item.task_title?.trim() || `Task #${item.task_id}`;
}
</script>

<template>
  <AdminListSkeleton v-if="loading" label="Loading sync queue" />

  <EmptyState v-else-if="items.length === 0" description="sync queue is clear" />

  <div v-else class="min-w-0">
    <AdminDataTable table-label="sync queue">
      <template #header>
        <th :class="ADMIN_TH_CLASS" scope="col">status</th>
        <th :class="ADMIN_TH_CLASS" scope="col">task</th>
        <th :class="ADMIN_TH_CLASS" scope="col">action</th>
        <th :class="[ADMIN_TH_CLASS, 'text-right']" scope="col">attempts</th>
        <th :class="ADMIN_TH_CLASS" scope="col">next retry</th>
        <th :class="[ADMIN_TH_CLASS, 'w-px text-right']" scope="col">actions</th>
      </template>
      <AdminDataRow
        v-for="item in items"
        :key="item.id"
        :interactive="false"
        :expandable="Boolean(item.last_error)"
        :expanded="expandedIds.has(item.id)"
        nested-interactive
        :col-span="6"
      >
        <td :class="ADMIN_TD_CLASS">
          <StatusBadge
            :label="statusLabel(item.status)"
            :class-name="statusBadgeClass(item.status)"
          />
        </td>
        <th :class="ADMIN_TH_ROW_CLASS" scope="row">
          <span class="truncate" :title="syncPrimary(item)">{{ syncPrimary(item) }}</span>
        </th>
        <td :class="ADMIN_TD_MUTED_CLASS">{{ item.action }}</td>
        <td :class="[ADMIN_TD_MUTED_CLASS, 'text-right tabular-nums']">{{ item.attempts }}</td>
        <td :class="ADMIN_TD_MUTED_CLASS">
          {{ item.next_retry_at ? formatDate(item.next_retry_at) : "—" }}
        </td>
        <template #actions>
          <BaseButton
            v-if="item.last_error"
            variant="ghost"
            size="sm"
            :icon="false"
            class="gap-1.5"
            :aria-expanded="expandedIds.has(item.id)"
            @click="toggleExpanded(item.id)"
          >
            <ChevronIcon :open="expandedIds.has(item.id)" class-name="size-3.5 shrink-0" />
            {{ expandedIds.has(item.id) ? "hide error" : "show error" }}
          </BaseButton>
          <BaseButton
            v-if="canMutate && item.status === 'failed'"
            variant="ghost"
            quiet
            size="sm"
            :icon="false"
            class="gap-1.5"
            aria-label="retry sync"
            @click="emit('retry', item.task_id)"
          >
            <SyncIcon class-name="size-3.5" />
            retry
          </BaseButton>
        </template>
        <template #detail>
          <p class="break-words text-status-error">{{ item.last_error }}</p>
        </template>
      </AdminDataRow>
    </AdminDataTable>
  </div>
</template>
