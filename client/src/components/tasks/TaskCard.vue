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
      <StatusBadge
        class="w-[9.5rem] justify-center"
        :label="statusLabel(task.status)"
        :class-name="statusBadgeClass(task.status)"
      />
    </template>
    <template #primary>
      <span class="lowercase" :title="task.title">{{ task.title }}</span>
    </template>
    <template #meta>
      <span v-if="task.location" class="inline-flex min-w-0 items-center gap-1 lowercase">
        <LocationIcon class-name="size-3.5 shrink-0" />
        <span class="truncate">{{ task.location }}</span>
      </span>
      <span
        v-if="task.google_event_id"
        class="inline-flex text-accent-blue"
        title="Synced to Google Calendar"
        aria-label="Synced to Google Calendar"
      >
        <SyncIcon class-name="size-4" />
      </span>
    </template>
    <template #time>{{ formatDate(task.scheduled_at) }}</template>
    <template #actions>
      <IconEditButton aria-label="edit task" @click="emit('select', task.id)" />
    </template>
  </AdminListRow>
</template>
