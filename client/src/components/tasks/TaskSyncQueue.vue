<script setup lang="ts">
import { ref } from "vue";

import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
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

function syncMeta(item: SyncQueueItem): string {
  const parts = [`${item.action}`, `attempts ${item.attempts}`];
  if (item.next_retry_at) {
    parts.push(`retry ${formatDate(item.next_retry_at)}`);
  }
  return parts.join(" · ");
}
</script>

<template>
  <AdminListSkeleton v-if="loading" label="Loading sync queue" />

  <div v-else-if="items.length === 0" class="py-8 text-center text-sm text-surface-mid">
    Sync queue is clear.
  </div>

  <div v-else class="space-y-1">
    <AdminListRow
      v-for="item in items"
      :key="item.id"
      :interactive="Boolean(item.last_error)"
      :expandable="Boolean(item.last_error)"
      :expanded="expandedIds.has(item.id)"
      :hoverable="Boolean(item.last_error)"
      :nested-interactive="canMutate && item.status === 'failed'"
      @click="item.last_error && toggleExpanded(item.id)"
    >
      <template #badge>
        <StatusBadge
          :label="statusLabel(item.status)"
          :class-name="statusBadgeClass(item.status)"
        />
      </template>
      <template #primary>Task #{{ item.task_id }}</template>
      <template #meta>
        <span>{{ syncMeta(item) }}</span>
      </template>
      <template #actions>
        <BaseButton
          v-if="canMutate && item.status === 'failed'"
          variant="ghost"
          size="sm"
          aria-label="Retry sync"
          @click="emit('retry', item.task_id)"
        >
          Retry
        </BaseButton>
        <span
          v-if="item.last_error && !expandedIds.has(item.id)"
          class="text-xs text-accent-golden"
          title="Has error — click to expand"
          aria-hidden="true"
        >
          ⚠
        </span>
      </template>
      <template #detail>
        <p class="break-words text-status-error">{{ item.last_error }}</p>
      </template>
    </AdminListRow>
  </div>
</template>
