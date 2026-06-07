<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseModal from "@/components/ui/BaseModal.vue";
import {
  statusActionLabel,
  statusBadgeClass,
  statusLabel,
  TASK_STATUSES,
  type TaskStatus,
} from "@/constants/taskStatus";
import type { TaskDetail } from "@/types";
import { formatDate, formatRelativeTime, formatScheduleDate } from "@/utils/format";

const props = defineProps<{
  task: TaskDetail;
  loading: boolean;
  canMutate?: boolean;
  statusUpdating?: boolean;
}>();

const emit = defineEmits<{
  close: [];
  retrySync: [taskId: number];
  updateStatus: [status: TaskStatus];
}>();

const availableStatuses = computed(() =>
  TASK_STATUSES.filter((status) => status !== props.task.status),
);

const schedule = computed(() => formatScheduleDate(props.task.scheduled_at));

const primaryActionStatus = computed((): TaskStatus | null =>
  props.task.status === "pending" ? "completed" : null,
);

function actionVariant(status: TaskStatus): "primary" | "ghost" {
  return status === primaryActionStatus.value ? "primary" : "ghost";
}
</script>

<template>
  <BaseModal :title="task.title" max-width="md" @close="emit('close')">
    <div v-if="loading" class="space-y-3 animate-pulse">
      <div class="h-6 w-24 bg-surface-border rounded" />
      <div class="h-4 w-full bg-surface-border rounded" />
      <div class="h-4 w-3/4 bg-surface-border rounded" />
    </div>

    <div v-else class="space-y-5 max-h-[70vh] overflow-y-auto">
      <span
        :class="['text-xs px-2 py-1 rounded-full border inline-block', statusBadgeClass(task.status)]"
      >
        {{ statusLabel(task.status) }}
      </span>

      <section>
        <h3 class="text-sm font-medium text-surface-mid mb-1">When</h3>
        <p class="text-sm text-surface-light">{{ schedule.headline }}</p>
        <p v-if="schedule.detail" class="text-xs text-surface-mid mt-0.5">{{ schedule.detail }}</p>
      </section>

      <section v-if="task.location">
        <h3 class="text-sm font-medium text-surface-mid mb-1">Where</h3>
        <p class="text-sm text-surface-light">@ {{ task.location }}</p>
      </section>

      <section v-if="task.description">
        <h3 class="text-sm font-medium text-surface-mid mb-1">About</h3>
        <p class="text-sm text-surface-light whitespace-pre-wrap">{{ task.description }}</p>
      </section>

      <section v-if="task.reminders.length" class="border-t border-surface-border pt-4">
        <h3 class="text-sm font-medium text-surface-mid mb-2">Reminders</h3>
        <ul class="space-y-2">
          <li
            v-for="reminder in task.reminders"
            :key="reminder.id"
            class="text-sm flex justify-between gap-3"
          >
            <span class="text-surface-light">
              {{ formatScheduleDate(reminder.remind_at).headline }}
            </span>
            <span
              :class="[
                'text-xs px-2 py-0.5 rounded-full shrink-0',
                reminder.sent
                  ? 'text-green-400 bg-green-400/10'
                  : 'text-yellow-400 bg-yellow-400/10',
              ]"
            >
              {{ reminder.sent ? "Delivered" : "Upcoming" }}
            </span>
          </li>
        </ul>
      </section>

      <section v-if="task.status_history.length" class="border-t border-surface-border pt-4">
        <h3 class="text-sm font-medium text-surface-mid mb-2">What changed</h3>
        <ul class="space-y-2">
          <li
            v-for="entry in task.status_history"
            :key="entry.id"
            class="text-sm text-surface-mid"
          >
            <span class="text-surface-light">{{ statusLabel(entry.old_status) }}</span>
            <span class="mx-1">&rarr;</span>
            <span class="text-surface-light">{{ statusLabel(entry.new_status) }}</span>
            <span class="ml-2 text-xs opacity-70">{{ formatRelativeTime(entry.changed_at) }}</span>
          </li>
        </ul>
      </section>

      <section v-if="canMutate" class="border-t border-surface-border pt-4 space-y-3">
        <div v-if="task.google_event_id" class="flex items-center gap-2">
          <span class="text-xs px-2 py-0.5 rounded-full text-accent-blue bg-accent-blue/10">
            Synced to Google Calendar
          </span>
        </div>
        <BaseButton variant="ghost" size="sm" @click="emit('retrySync', task.id)">
          Try syncing again
        </BaseButton>
      </section>

      <section v-if="canMutate" class="border-t border-surface-border pt-4">
        <h3 class="text-sm font-medium text-surface-mid mb-2">Actions</h3>
        <div class="flex flex-wrap gap-2">
          <BaseButton
            v-for="status in availableStatuses"
            :key="status"
            :variant="actionVariant(status)"
            size="sm"
            :disabled="statusUpdating"
            @click="emit('updateStatus', status)"
          >
            {{ statusActionLabel(status) }}
          </BaseButton>
        </div>
      </section>

      <details v-if="canMutate" class="border-t border-surface-border pt-4 text-sm text-surface-mid">
        <summary class="cursor-pointer hover:text-surface-light select-none">
          Technical details
        </summary>
        <dl class="mt-2 space-y-1 text-xs">
          <div v-if="task.google_event_id">
            <dt class="inline font-medium">Event ID:</dt>
            <dd class="inline ml-1 break-all">{{ task.google_event_id }}</dd>
          </div>
          <div>
            <dt class="inline font-medium">Created:</dt>
            <dd class="inline ml-1">{{ formatDate(task.created_at) }}</dd>
          </div>
        </dl>
      </details>
    </div>
  </BaseModal>
</template>
