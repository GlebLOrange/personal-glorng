<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import { statusBadgeClass, statusLabel } from "@/constants/taskStatus";
import { formatDate } from "@/utils/format";
import type { SyncQueueItem } from "@/types";

defineProps<{
  items: SyncQueueItem[];
  loading: boolean;
  canMutate?: boolean;
}>();

const emit = defineEmits<{ retry: [taskId: number] }>();

const skeletonRows = 3;
</script>

<template>
  <div v-if="loading" class="space-y-3">
    <Card v-for="n in skeletonRows" :key="n" class="animate-pulse">
      <div class="h-4 w-28 bg-surface-border rounded mb-2" />
      <div class="h-3 w-full bg-surface-border rounded" />
    </Card>
  </div>

  <div v-else-if="items.length === 0" class="text-surface-mid text-sm text-center py-8">
    Sync queue is clear.
  </div>

  <div v-else class="space-y-3">
    <Card v-for="item in items" :key="item.id">
      <div class="flex justify-between items-start gap-3">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1 flex-wrap">
            <span class="text-surface-light font-bold text-sm">Task #{{ item.task_id }}</span>
            <span class="text-xs text-accent-blue">{{ item.action }}</span>
            <span
              :class="[
                'text-[10px] px-2 py-0.5 rounded-full border',
                statusBadgeClass(item.status),
              ]"
            >
              {{ statusLabel(item.status) }}
            </span>
          </div>
          <div class="text-xs text-surface-mid">
            Attempts: {{ item.attempts }}
            <span v-if="item.next_retry_at">
              · Next retry: {{ formatDate(item.next_retry_at) }}
            </span>
          </div>
          <div v-if="item.last_error" class="text-xs text-red-400 mt-1 break-words">
            {{ item.last_error }}
          </div>
        </div>
        <BaseButton
          v-if="canMutate && item.status === 'failed'"
          variant="ghost"
          size="sm"
          @click="emit('retry', item.task_id)"
        >
          Retry
        </BaseButton>
      </div>
    </Card>
  </div>
</template>
