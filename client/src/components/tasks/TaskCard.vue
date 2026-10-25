<script setup lang="ts">
import LocationIcon from "@/components/icons/LocationIcon.vue";
import SyncIcon from "@/components/icons/SyncIcon.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import {
  ADMIN_ACTIONS_CLASS,
  ADMIN_TD_ACTIONS_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TH_ROW_CLASS,
  ADMIN_TR_CLASS,
} from "@/constants/adminDataTable";
import { statusBadgeClass, statusLabel } from "@/constants/taskStatus";
import { formatDate } from "@/utils/format";
import type { TaskItem } from "@/types";

defineProps<{
  task: TaskItem;
}>();

const emit = defineEmits<{ select: [id: number] }>();
</script>

<template>
  <tr
    :class="[ADMIN_TR_CLASS, 'cursor-pointer']"
    role="button"
    tabindex="0"
    @click="emit('select', task.id)"
    @keydown.enter.prevent="emit('select', task.id)"
    @keydown.space.prevent="emit('select', task.id)"
  >
    <td :class="ADMIN_TD_CLASS">
      <StatusBadge
        class="w-[9.5rem] justify-center"
        :label="statusLabel(task.status)"
        :class-name="statusBadgeClass(task.status)"
      />
    </td>
    <td :class="ADMIN_TD_MUTED_CLASS">{{ formatDate(task.scheduled_at) }}</td>
    <th :class="ADMIN_TH_ROW_CLASS" scope="row">
      <div class="flex min-w-0 items-center gap-1.5">
        <p class="min-w-0 truncate text-sm lowercase text-surface-light" :title="task.title">
          {{ task.title }}
        </p>
        <span
          v-if="task.google_event_id"
          class="inline-flex shrink-0 text-accent-coral"
          title="synced to Google Calendar"
          aria-label="synced to Google Calendar"
        >
          <SyncIcon class-name="size-4" />
        </span>
      </div>
      <p
        v-if="task.location"
        class="mt-0.5 flex min-w-0 items-center gap-1 text-xs lowercase text-surface-mid"
      >
        <LocationIcon class-name="size-3.5 shrink-0" />
        <span class="truncate" :title="task.location">{{ task.location }}</span>
      </p>
    </th>
    <td :class="ADMIN_TD_ACTIONS_CLASS" @click.stop @keydown.stop>
      <div :class="ADMIN_ACTIONS_CLASS">
        <IconEditButton aria-label="edit task" @click="emit('select', task.id)" />
      </div>
    </td>
  </tr>
</template>
