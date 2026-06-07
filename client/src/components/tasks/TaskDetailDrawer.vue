<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { statusBadgeClass, statusLabel, TASK_STATUSES, type TaskStatus } from "@/constants/taskStatus";
import { formatDate } from "@/utils/format";
import type { TaskDetail } from "@/types";

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
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="task" class="fixed inset-0 z-50 flex justify-end" @click.self="emit('close')">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="emit('close')" />
        <div
          class="relative w-full max-w-md bg-surface-dark border-l border-surface-border overflow-y-auto p-6"
        >
          <div class="flex justify-between items-start mb-6">
            <h2 class="text-lg font-bold text-surface-light pr-4">{{ task.title }}</h2>
            <button
              type="button"
              class="text-surface-mid hover:text-surface-light text-xl leading-none shrink-0"
              aria-label="Close"
              @click="emit('close')"
            >
              &times;
            </button>
          </div>

          <div v-if="loading" class="space-y-3 animate-pulse">
            <div class="h-6 w-24 bg-surface-border rounded" />
            <div class="h-4 w-full bg-surface-border rounded" />
            <div class="h-4 w-3/4 bg-surface-border rounded" />
          </div>

          <div v-else class="space-y-4">
            <div>
              <span
                :class="[
                  'text-xs px-2 py-1 rounded-full border',
                  statusBadgeClass(task.status),
                ]"
              >
                {{ statusLabel(task.status) }}
              </span>
            </div>

            <div class="text-xs text-surface-mid space-y-1">
              <div>Scheduled: {{ formatDate(task.scheduled_at) }}</div>
              <div v-if="task.location">Location: {{ task.location }}</div>
              <div v-if="task.description">Notes: {{ task.description }}</div>
              <div v-if="task.google_event_id">Google Event: {{ task.google_event_id }}</div>
              <div>Created: {{ formatDate(task.created_at) }}</div>
            </div>

            <div v-if="task.reminders.length">
              <h3 class="text-sm font-bold text-surface-light mb-2 border-t border-surface-border pt-4">
                Reminders
              </h3>
              <div class="space-y-2">
                <div
                  v-for="reminder in task.reminders"
                  :key="reminder.id"
                  class="text-xs text-surface-mid flex justify-between"
                >
                  <span>{{ formatDate(reminder.remind_at) }}</span>
                  <span :class="reminder.sent ? 'text-green-400' : 'text-yellow-400'">
                    {{ reminder.sent ? "sent" : "pending" }}
                  </span>
                </div>
              </div>
            </div>

            <div v-if="task.status_history.length">
              <h3 class="text-sm font-bold text-surface-light mb-2 border-t border-surface-border pt-4">
                Status history
              </h3>
              <div class="space-y-2">
                <div
                  v-for="entry in task.status_history"
                  :key="entry.id"
                  class="text-xs text-surface-mid"
                >
                  <span class="text-red-400">{{ entry.old_status }}</span>
                  <span class="mx-1">&rarr;</span>
                  <span class="text-green-400">{{ entry.new_status }}</span>
                  <span class="ml-2 opacity-60">{{ formatDate(entry.changed_at) }}</span>
                </div>
              </div>
            </div>

            <div v-if="canMutate" class="border-t border-surface-border pt-4 space-y-3">
              <h3 class="text-sm font-bold text-surface-light">Sync</h3>
              <BaseButton variant="ghost" size="sm" @click="emit('retrySync', task.id)">
                Retry calendar sync
              </BaseButton>
            </div>

            <div v-if="canMutate" class="border-t border-surface-border pt-4">
              <h3 class="text-sm font-bold text-surface-light mb-2">Actions</h3>
              <div class="flex flex-wrap gap-2">
                <BaseButton
                  v-for="status in availableStatuses"
                  :key="status"
                  variant="ghost"
                  size="sm"
                  :disabled="statusUpdating"
                  @click="emit('updateStatus', status)"
                >
                  Set {{ statusLabel(status) }}
                </BaseButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
