<script setup lang="ts">
import { ref } from "vue";

import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
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

  <EmptyState v-else-if="items.length === 0" description="Sync queue is clear." />

  <div v-else class="space-y-1">
    <AdminListRow
      v-for="item in items"
      :key="item.id"
      :interactive="false"
      :expandable="Boolean(item.last_error)"
      :expanded="expandedIds.has(item.id)"
      :hoverable="Boolean(item.last_error)"
      :nested-interactive="true"
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
          v-if="item.last_error"
          variant="ghost"
          size="sm"
          :aria-expanded="expandedIds.has(item.id)"
          @click="toggleExpanded(item.id)"
        >
          {{ expandedIds.has(item.id) ? "hide error" : "show error" }}
        </BaseButton>
        <BaseButton
          v-if="canMutate && item.status === 'failed'"
          variant="ghost"
          size="sm"
          aria-label="Retry sync"
          @click="emit('retry', item.task_id)"
        >
          Retry
        </BaseButton>
      </template>
      <template #detail>
        <p class="break-words text-status-error">{{ item.last_error }}</p>
      </template>
    </AdminListRow>
  </div>
</template>
