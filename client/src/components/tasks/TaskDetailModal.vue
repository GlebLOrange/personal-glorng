<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseModal from "@/components/ui/BaseModal.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
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
      <StatusBadge :label="statusLabel(task.status)" :class-name="statusBadgeClass(task.status)" />

      <section class="space-y-2">
        <div class="flex min-w-0 items-baseline gap-2 text-sm">
          <span class="shrink-0 text-surface-mid">when</span>
          <span
            class="min-w-4 flex-1 translate-y-[-0.15em] border-b border-dotted border-surface-border/50"
            aria-hidden="true"
          />
          <span class="shrink-0 text-right text-surface-light">{{ schedule.headline }}</span>
        </div>
        <p v-if="schedule.detail" class="text-right text-xs text-surface-mid">{{ schedule.detail }}</p>

        <div v-if="task.location" class="flex min-w-0 items-baseline gap-2 text-sm">
          <span class="shrink-0 text-surface-mid">where</span>
          <span
            class="min-w-4 flex-1 translate-y-[-0.15em] border-b border-dotted border-surface-border/50"
            aria-hidden="true"
          />
          <span class="shrink-0 text-right text-surface-light">@{{ task.location }}</span>
        </div>
      </section>

      <section v-if="task.description">
        <div class="mb-1 flex min-w-0 items-baseline gap-2 text-sm">
          <span class="shrink-0 text-surface-mid">about</span>
          <span
            class="min-w-4 flex-1 translate-y-[-0.15em] border-b border-dotted border-surface-border/50"
            aria-hidden="true"
          />
        </div>
        <p class="text-sm text-surface-light whitespace-pre-wrap">{{ task.description }}</p>
      </section>

      <section v-if="task.reminders.length" class="border-t border-surface-border pt-4">
        <h3 class="mb-2 text-sm font-medium text-surface-mid">reminders</h3>
        <ul class="space-y-2">
          <li
            v-for="reminder in task.reminders"
            :key="reminder.id"
            class="flex min-w-0 items-baseline gap-2 text-sm"
          >
            <span class="min-w-0 flex-1 text-surface-light">
              {{ formatScheduleDate(reminder.remind_at).headline }}
            </span>
            <span
              :class="[
                'shrink-0 text-xs px-2 py-0.5 rounded-full',
                reminder.sent
                  ? 'text-status-success bg-status-success/10'
                  : 'text-status-warning bg-status-warning/10',
              ]"
            >
              {{ reminder.sent ? "delivered" : "upcoming" }}
            </span>
          </li>
        </ul>
      </section>

      <section v-if="task.status_history.length" class="border-t border-surface-border pt-4">
        <h3 class="mb-2 text-sm font-medium text-surface-mid">what changed</h3>
        <ul class="space-y-2">
          <li
            v-for="entry in task.status_history"
            :key="entry.id"
            class="flex flex-wrap items-center gap-2 text-sm"
          >
            <StatusBadge
              :label="statusLabel(entry.old_status)"
              :class-name="statusBadgeClass(entry.old_status)"
            />
            <span class="text-surface-mid">&rarr;</span>
            <StatusBadge
              :label="statusLabel(entry.new_status)"
              :class-name="statusBadgeClass(entry.new_status)"
            />
            <span class="ml-auto text-xs text-surface-mid">{{
              formatRelativeTime(entry.changed_at)
            }}</span>
          </li>
        </ul>
      </section>

      <section v-if="canMutate" class="space-y-3 border-t border-surface-border pt-4">
        <div v-if="task.google_event_id" class="flex items-center gap-2">
          <span class="rounded-full bg-accent-blue/10 px-2 py-0.5 text-xs text-accent-blue">
            synced to google calendar
          </span>
        </div>
        <BaseButton
          v-else
          variant="ghost"
          size="sm"
          @click="emit('retrySync', task.id)"
        >
          try syncing again
        </BaseButton>
      </section>

      <section v-if="canMutate" class="border-t border-surface-border pt-4">
        <h3 class="mb-2 text-sm font-medium text-surface-mid">actions</h3>
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

      <details
        v-if="canMutate"
        class="border-t border-surface-border pt-4 text-sm text-surface-mid"
      >
        <summary class="cursor-pointer select-none hover:text-surface-light">
          technical details
        </summary>
        <dl class="mt-2 space-y-1 text-xs">
          <div v-if="task.google_event_id">
            <dt class="inline font-medium">event id:</dt>
            <dd class="ml-1 inline break-all">{{ task.google_event_id }}</dd>
          </div>
          <div>
            <dt class="inline font-medium">created:</dt>
            <dd class="ml-1 inline">{{ formatDate(task.created_at) }}</dd>
          </div>
        </dl>
      </details>
    </div>
  </BaseModal>
</template>
