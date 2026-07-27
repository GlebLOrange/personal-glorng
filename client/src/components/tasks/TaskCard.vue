<script setup lang="ts">
import AdminListRow from "@/components/admin/AdminListRow.vue";
import LocationIcon from "@/components/icons/LocationIcon.vue";
import SyncIcon from "@/components/icons/SyncIcon.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { statusBadgeClass, statusLabel } from "@/constants/taskStatus";
import { formatDate } from "@/utils/format";
import type { TaskItem } from "@/types";

defineProps<{
  task: TaskItem;
}>();

const emit = defineEmits<{ select: [id: number] }>();
</script>

<template>
  <AdminListRow
    interactive
    nested-interactive
    reveal-actions-on-hover
    :status-class="statusBadgeClass(task.status)"
    @click="emit('select', task.id)"
  >
    <template #badge>
      <div class="flex items-center gap-2">
        <StatusBadge
          class="w-[9.5rem] justify-center"
          :label="statusLabel(task.status)"
          :class-name="statusBadgeClass(task.status)"
        />
        <span class="whitespace-nowrap text-xs lowercase text-surface-muted">
          {{ formatDate(task.scheduled_at) }}
        </span>
        <span v-if="task.location" class="inline-flex min-w-0 items-center gap-1 lowercase">
          <LocationIcon class-name="size-3.5 shrink-0" />
          <span class="max-w-[8rem] truncate text-xs text-surface-muted">{{ task.location }}</span>
        </span>
        <span
          v-if="task.google_event_id"
          class="inline-flex text-accent-blue"
          title="synced to Google Calendar"
          aria-label="synced to Google Calendar"
        >
          <SyncIcon class-name="size-4" />
        </span>
      </div>
    </template>
    <template #primary>
      <span class="lowercase" :title="task.title">{{ task.title }}</span>
    </template>
    <template #actions>
      <IconEditButton aria-label="edit task" @click="emit('select', task.id)" />
    </template>
  </AdminListRow>
</template>
