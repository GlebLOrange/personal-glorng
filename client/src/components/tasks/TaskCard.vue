<script setup lang="ts">
import { Card } from "@/components/ui/card";
import { statusBadgeClass, statusLabel } from "@/constants/taskStatus";
import { formatDate } from "@/utils/format";
import type { TaskItem } from "@/types";

defineProps<{
  task: TaskItem;
}>();

const emit = defineEmits<{ select: [id: number] }>();
</script>

<template>
  <Card
    as="button"
    type="button"
    variant="compact"
    hoverable
    interactive
    class="w-full text-left"
    @click="emit('select', task.id)"
  >
    <div class="flex justify-between items-start gap-3">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2 mb-1 flex-wrap">
          <span class="text-surface-light font-bold text-sm truncate">{{ task.title }}</span>
          <span
            :class="[
              'text-[10px] px-2 py-0.5 rounded-full border shrink-0',
              statusBadgeClass(task.status),
            ]"
          >
            {{ statusLabel(task.status) }}
          </span>
        </div>
        <div class="text-xs text-surface-mid">{{ formatDate(task.scheduled_at) }}</div>
        <div v-if="task.location" class="text-xs text-surface-mid mt-1">@ {{ task.location }}</div>
      </div>
      <div
        v-if="task.google_event_id"
        class="text-xs text-accent-blue shrink-0"
        title="Synced to Google Calendar"
      >
        GCal
      </div>
    </div>
  </Card>
</template>
