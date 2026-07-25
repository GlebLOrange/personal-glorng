<script setup lang="ts">
import { computed, ref, watch } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDropdownMenu from "@/components/ui/BaseDropdownMenu.vue";
import BaseDropdownMenuItem from "@/components/ui/BaseDropdownMenuItem.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import ToolIcon from "@/components/icons/ToolIcon.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import {
  statusActionLabel,
  statusBadgeClass,
  statusLabel,
  statusMenuItemClass,
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

const technicalOpen = ref(false);

const availableStatuses = computed(() =>
  props.task ? TASK_STATUSES.filter((status) => status !== props.task.status) : [],
);

const schedule = computed(() => (props.task ? formatScheduleDate(props.task.scheduled_at) : null));

const primaryActionStatus = computed((): TaskStatus | null =>
  props.task?.status === "pending" || props.task?.status === "not_completed" ? "completed" : null,
);

const menuStatuses = computed(() =>
  availableStatuses.value.filter((status) => status !== primaryActionStatus.value),
);

const recentStatusHistory = computed(() => (props.task?.status_history ?? []).slice(-4));

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) technicalOpen.value = false;
  },
);
</script>

<template>
  <BaseDrawer :open="open" :title="task?.title ?? 'Task'" max-width="md" @close="emit('close')">
    <template v-if="task" #title="{ titleId }">
      <div class="flex min-w-0 flex-col gap-2">
        <StatusBadge
          size="sm"
          class="inline-flex h-8 items-center"
          :label="statusLabel(task.status)"
          :class-name="statusBadgeClass(task.status)"
        />
        <h2 :id="titleId" class="truncate text-lg font-bold text-surface-light">
          {{ task.title }}
        </h2>
      </div>
    </template>

    <div v-if="loading || !task" class="space-y-3 animate-pulse">
      <div class="h-4 w-full rounded bg-surface-border" />
      <div class="h-4 w-3/4 rounded bg-surface-border" />
    </div>

    <div v-else class="space-y-5">
      <section class="space-y-2">
        <div class="space-y-1">
          <div class="flex min-w-0 items-baseline justify-between gap-3 text-sm">
            <span class="shrink-0 text-surface-mid">deadline</span>
            <span class="min-w-0 text-right text-surface-light">{{ schedule?.headline }}</span>
          </div>
          <p v-if="schedule?.detail" class="text-right text-xs text-surface-mid">
            {{ schedule.detail }}
          </p>
        </div>

        <div v-if="task.location" class="flex min-w-0 items-baseline justify-between gap-3 text-sm">
          <span class="shrink-0 text-surface-mid">location</span>
          <span class="min-w-0 text-right text-surface-light">@{{ task.location }}</span>
        </div>
      </section>

      <section
        v-if="task.description"
        class="flex min-w-0 items-baseline justify-between gap-3 text-sm"
      >
        <span class="shrink-0 text-surface-mid">about</span>
        <p class="min-w-0 whitespace-pre-wrap text-right text-surface-light">
          {{ task.description }}
        </p>
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

      <section v-if="recentStatusHistory.length" class="border-t border-surface-border pt-4">
        <ul class="space-y-2">
          <li
            v-for="entry in recentStatusHistory"
            :key="entry.id"
            class="flex flex-wrap items-center gap-2 text-sm"
          >
            <StatusBadge
              :label="statusLabel(entry.old_status)"
              :class-name="statusBadgeClass(entry.old_status)"
            />
            <ChevronIcon direction="right" class-name="size-3.5 text-surface-mid" />
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
          quiet
          size="sm"
          class="gap-1.5 hover:enabled:!bg-accent-blue/10 hover:enabled:!text-accent-blue focus-visible:!text-accent-blue"
          title="Try syncing again"
          @click="emit('retrySync', task.id)"
        >
          <ToolIcon slug="sync" class="h-4 w-4" />
          try syncing again
        </BaseButton>
      </section>

      <section v-if="canMutate" class="space-y-2 border-t border-surface-border pt-4">
        <BaseButton
          variant="ghost"
          quiet
          size="sm"
          class="gap-1.5"
          :selected="technicalOpen"
          :aria-expanded="technicalOpen"
          aria-controls="task-technical-details"
          @click="technicalOpen = !technicalOpen"
        >
          technical details
          <ChevronIcon :open="technicalOpen" />
        </BaseButton>
        <dl v-if="technicalOpen" id="task-technical-details" class="space-y-1 text-xs">
          <div
            v-if="task.google_event_id"
            class="flex min-w-0 items-baseline justify-between gap-3"
          >
            <dt class="shrink-0 text-surface-mid">event id</dt>
            <dd class="min-w-0 break-all text-right text-surface-light">
              {{ task.google_event_id }}
            </dd>
          </div>
          <div class="flex min-w-0 items-baseline justify-between gap-3">
            <dt class="shrink-0 text-surface-mid">created</dt>
            <dd class="min-w-0 text-right text-surface-light">
              {{ formatDate(task.created_at) }}
            </dd>
          </div>
          <div class="flex min-w-0 items-baseline justify-between gap-3">
            <dt class="shrink-0 text-surface-mid">updated</dt>
            <dd class="min-w-0 text-right text-surface-light">
              {{ formatDate(task.updated_at) }}
            </dd>
          </div>
        </dl>
      </section>
    </div>

    <template v-if="canMutate && task" #footer>
      <div class="flex w-full flex-wrap items-center gap-2">
        <BaseDropdownMenu v-if="menuStatuses.length" placement="top" aria-label="more actions">
          <template #trigger="{ open: menuOpen }">
            <span class="inline-flex items-center gap-1.5 px-2 text-sm text-surface-mid">
              more actions
              <ChevronIcon :open="menuOpen" />
            </span>
          </template>
          <template #default="{ close: closeMenu }">
            <BaseDropdownMenuItem
              v-for="status in menuStatuses"
              :key="status"
              :color-class="statusMenuItemClass(status)"
              @select="
                closeMenu();
                if (!statusUpdating) emit('updateStatus', status);
              "
            >
              {{ statusActionLabel(status) }}
            </BaseDropdownMenuItem>
          </template>
        </BaseDropdownMenu>
        <ToolbarPillButton
          v-if="primaryActionStatus"
          family="2xx"
          class="ml-auto"
          :disabled="statusUpdating"
          @click="emit('updateStatus', primaryActionStatus)"
        >
          {{ statusActionLabel(primaryActionStatus) }}
        </ToolbarPillButton>
      </div>
    </template>
  </BaseDrawer>
</template>
