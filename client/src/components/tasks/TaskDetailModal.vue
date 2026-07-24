<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDropdownMenu from "@/components/ui/BaseDropdownMenu.vue";
import BaseDropdownMenuItem from "@/components/ui/BaseDropdownMenuItem.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import ToolIcon from "@/components/icons/ToolIcon.vue";
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
  open: boolean;
  task: TaskDetail | null;
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
  props.task
    ? TASK_STATUSES.filter((status) => status !== props.task!.status)
    : [],
);

const schedule = computed(() =>
  props.task ? formatScheduleDate(props.task.scheduled_at) : null,
);

const primaryActionStatus = computed((): TaskStatus | null =>
  props.task?.status === "pending" || props.task?.status === "not_completed"
    ? "completed"
    : null,
);

const menuStatuses = computed(() =>
  availableStatuses.value.filter((status) => status !== primaryActionStatus.value),
);
</script>

<template>
  <BaseDrawer
    :open="open"
    :title="task?.title ?? 'Task'"
    max-width="md"
    @close="emit('close')"
  >
    <template v-if="task" #title>
      <div class="flex min-w-0 flex-col gap-2">
        <StatusBadge
          size="lg"
          :label="statusLabel(task.status)"
          :class-name="statusBadgeClass(task.status)"
        />
        <h2 class="truncate text-lg font-bold text-surface-light">{{ task.title }}</h2>
      </div>
    </template>

    <div v-if="loading || !task" class="space-y-3 animate-pulse">
      <div class="h-4 w-full rounded bg-surface-border" />
      <div class="h-4 w-3/4 rounded bg-surface-border" />
    </div>

    <div v-else class="space-y-5">
      <section class="space-y-2">
        <div class="flex min-w-0 items-baseline gap-2 text-sm">
          <span class="shrink-0 text-surface-mid">deadline</span>
          <span
            class="min-w-4 flex-1 translate-y-[-0.15em] border-b border-dotted border-surface-border/50"
            aria-hidden="true"
          />
          <span class="shrink-0 text-right text-surface-light">{{ schedule?.headline }}</span>
        </div>
        <p v-if="schedule?.detail" class="text-right text-xs text-surface-mid">
          {{ schedule.detail }}
        </p>

        <div v-if="task.location" class="flex min-w-0 items-baseline gap-2 text-sm">
          <span class="shrink-0 text-surface-mid">location</span>
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
        <p class="whitespace-pre-wrap text-sm text-surface-light">{{ task.description }}</p>
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
                'shrink-0 rounded-full px-2 py-0.5 text-xs',
                reminder.sent
                  ? 'bg-status-success/10 text-status-success'
                  : 'bg-status-warning/10 text-status-warning',
              ]"
            >
              {{ reminder.sent ? "delivered" : "upcoming" }}
            </span>
          </li>
        </ul>
      </section>

      <section v-if="task.status_history.length" class="border-t border-surface-border pt-4">
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
          <span
            class="inline-flex items-center gap-1.5 rounded-full bg-accent-blue/10 px-2 py-0.5 text-xs text-accent-blue"
            title="Synced to Google Calendar"
          >
            <ToolIcon slug="sync" class="h-3.5 w-3.5" />
            synced to google calendar
          </span>
        </div>
        <BaseButton
          v-else
          variant="ghost"
          size="sm"
          class="gap-1.5"
          title="Try syncing again"
          @click="emit('retrySync', task.id)"
        >
          <ToolIcon slug="sync" class="h-4 w-4" />
          try syncing again
        </BaseButton>
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
          <div>
            <dt class="inline font-medium">updated:</dt>
            <dd class="ml-1 inline">{{ formatDate(task.updated_at) }}</dd>
          </div>
        </dl>
      </details>
    </div>

    <template v-if="canMutate && task" #footer>
      <div class="flex flex-wrap items-center gap-2">
        <BaseButton
          v-if="primaryActionStatus"
          variant="primary"
          size="sm"
          :disabled="statusUpdating"
          @click="emit('updateStatus', primaryActionStatus)"
        >
          {{ statusActionLabel(primaryActionStatus) }}
        </BaseButton>
        <BaseDropdownMenu
          v-if="menuStatuses.length"
          placement="top"
          aria-label="more actions"
        >
          <template #trigger>
            <span class="px-2 text-sm">more actions</span>
          </template>
          <template #default="{ close: closeMenu }">
            <BaseDropdownMenuItem
              v-for="status in menuStatuses"
              :key="status"
              :destructive="status === 'cancelled' || status === 'not_completed'"
              @select="
                closeMenu();
                if (!statusUpdating) emit('updateStatus', status);
              "
            >
              {{ statusActionLabel(status) }}
            </BaseDropdownMenuItem>
          </template>
        </BaseDropdownMenu>
      </div>
    </template>
  </BaseDrawer>
</template>
