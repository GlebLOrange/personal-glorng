<script setup lang="ts">
import AdminListRow from "@/components/admin/AdminListRow.vue";
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
  <AdminListRow interactive @click="emit('select', task.id)">
    <template #badge>
      <StatusBadge
        :label="statusLabel(task.status)"
        :class-name="statusBadgeClass(task.status)"
      />
    </template>
    <template #primary>
      <span :title="task.title">{{ task.title }}</span>
    </template>
    <template #meta>
      <span v-if="task.location">@ {{ task.location }}</span>
    </template>
    <template #time>{{ formatDate(task.scheduled_at) }}</template>
    <template #actions>
      <span
        v-if="task.google_event_id"
        class="text-xs text-accent-blue"
        title="Synced to Google Calendar"
      >
        GCal
      </span>
    </template>
  </AdminListRow>
</template>
