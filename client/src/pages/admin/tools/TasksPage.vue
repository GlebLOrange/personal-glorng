<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { formatDate } from "@/utils/format";
import type {
  SyncQueueItem,
  TaskDetail,
  TaskItem,
  TaskStats,
} from "@/types";

type Tab = "tasks" | "sync" | "stats";

const activeTab = ref<Tab>("tasks");
const tasks = ref<TaskItem[]>([]);
const stats = ref<TaskStats | null>(null);
const syncQueue = ref<SyncQueueItem[]>([]);
const selectedTask = ref<TaskDetail | null>(null);
const filterStatus = ref("");
const loading = ref(false);
const showCreateForm = ref(false);
const saving = ref(false);
const createForm = ref({
  title: "",
  scheduled_at: "",
  description: "",
  location: "",
});
const { toast } = useNotify();

const statusColors: Record<string, string> = {
  pending: "text-yellow-400 bg-yellow-400/10 border-yellow-400/30",
  completed: "text-green-400 bg-green-400/10 border-green-400/30",
  not_completed: "text-red-400 bg-red-400/10 border-red-400/30",
  postponed: "text-blue-400 bg-blue-400/10 border-blue-400/30",
  cancelled: "text-surface-mid bg-surface-mid/10 border-surface-border",
  failed: "text-red-400 bg-red-400/10 border-red-400/30",
};

const filteredTasks = computed(() => {
  if (!filterStatus.value) return tasks.value;
  return tasks.value.filter((t) => t.status === filterStatus.value);
});

async function loadTasks(): Promise<void> {
  loading.value = true;
  try {
    const { data } = await api.get<TaskItem[]>("/tools/tasks");
    tasks.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load tasks", "error");
  } finally {
    loading.value = false;
  }
}

async function loadStats(): Promise<void> {
  try {
    const { data } = await api.get<TaskStats>("/tools/tasks/stats");
    stats.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load stats", "error");
  }
}

async function loadSyncQueue(): Promise<void> {
  try {
    const { data } = await api.get<SyncQueueItem[]>(
      "/tools/tasks/sync-queue",
    );
    syncQueue.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load sync queue", "error");
  }
}

async function openDetail(taskId: number): Promise<void> {
  try {
    const { data } = await api.get<TaskDetail>(`/tools/tasks/${taskId}`);
    selectedTask.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load task detail", "error");
  }
}

async function retrySync(taskId: number): Promise<void> {
  try {
    await api.post(`/tools/tasks/${taskId}/retry-sync`);
    toast("Sync retry queued", "success");
    await loadSyncQueue();
  } catch (err) {
    console.error(err);
    toast("Failed to retry sync", "error");
  }
}

function closeDetail(): void {
  selectedTask.value = null;
}

function openCreate(): void {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  createForm.value = {
    title: "",
    scheduled_at: now.toISOString().slice(0, 16),
    description: "",
    location: "",
  };
  showCreateForm.value = true;
}

async function createTask(): Promise<void> {
  if (!createForm.value.title.trim() || !createForm.value.scheduled_at) {
    toast("Title and scheduled time are required", "error");
    return;
  }
  saving.value = true;
  try {
    const scheduledAt = new Date(createForm.value.scheduled_at).toISOString();
    await api.post("/tools/tasks", {
      title: createForm.value.title.trim(),
      scheduled_at: scheduledAt,
      description: createForm.value.description.trim() || null,
      location: createForm.value.location.trim() || null,
    });
    toast("Task created", "success");
    showCreateForm.value = false;
    await loadTasks();
    await loadStats();
  } catch (err) {
    console.error(err);
    toast("Failed to create task", "error");
  } finally {
    saving.value = false;
  }
}

function switchTab(tab: Tab): void {
  activeTab.value = tab;
  if (tab === "stats") loadStats();
  if (tab === "sync") loadSyncQueue();
}

onMounted(() => {
  loadTasks();
  loadStats();
});
</script>

<template>
  <AdminPageLayout title="tasks" max-width="xl">
    <!-- Tab navigation -->
    <div class="flex gap-2 mb-6 border-b border-surface-border pb-2">
      <button
        v-for="tab in (['tasks', 'sync', 'stats'] as Tab[])"
        :key="tab"
        :class="[
          'px-3 py-1.5 text-xs font-mono rounded-lg transition-colors',
          activeTab === tab
            ? 'bg-accent-blue/20 text-accent-blue'
            : 'text-surface-mid hover:text-surface-light',
        ]"
        @click="switchTab(tab)"
      >
        {{ tab }}
      </button>
    </div>

    <!-- Stats -->
    <div
      v-if="activeTab === 'stats' && stats"
      class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
    >
      <BaseCard>
        <div class="text-2xl font-bold text-surface-light">
          {{ stats.total }}
        </div>
        <div class="text-xs text-surface-mid mt-1">Total</div>
      </BaseCard>
      <BaseCard>
        <div class="text-2xl font-bold text-yellow-400">
          {{ stats.pending }}
        </div>
        <div class="text-xs text-surface-mid mt-1">Pending</div>
      </BaseCard>
      <BaseCard>
        <div class="text-2xl font-bold text-green-400">
          {{ stats.completed }}
        </div>
        <div class="text-xs text-surface-mid mt-1">Completed</div>
      </BaseCard>
      <BaseCard>
        <div class="text-2xl font-bold text-red-400">
          {{ stats.failed_syncs }}
        </div>
        <div class="text-xs text-surface-mid mt-1">Failed syncs</div>
      </BaseCard>
    </div>

    <!-- Tasks list -->
    <div v-if="activeTab === 'tasks'">
      <div class="flex gap-2 mb-4 items-center justify-between">
        <select
          v-model="filterStatus"
          class="bg-surface-card border border-surface-border rounded-lg px-3 py-1.5 text-xs font-mono text-surface-light focus:outline-none focus:border-accent-blue"
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
          <option value="not_completed">Not completed</option>
          <option value="postponed">Postponed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <BaseButton variant="primary" size="sm" @click="openCreate">+ New task</BaseButton>
      </div>

      <div class="space-y-3">
        <BaseCard
          v-for="task in filteredTasks"
          :key="task.id"
          hoverable
          class="cursor-pointer"
          @click="openDetail(task.id)"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-surface-light font-bold text-sm truncate">
                  {{ task.title }}
                </span>
                <span
                  :class="[
                    'text-[10px] px-2 py-0.5 rounded-full border',
                    statusColors[task.status] ?? 'text-surface-mid',
                  ]"
                >
                  {{ task.status }}
                </span>
              </div>
              <div class="text-xs text-surface-mid">
                {{ formatDate(task.scheduled_at) }}
              </div>
              <div
                v-if="task.location"
                class="text-xs text-surface-mid mt-1"
              >
                @ {{ task.location }}
              </div>
            </div>
            <div
              v-if="task.google_event_id"
              class="text-xs text-accent-blue ml-4"
              title="Synced to Google Calendar"
            >
              GCal
            </div>
          </div>
        </BaseCard>

        <p
          v-if="filteredTasks.length === 0 && !loading"
          class="text-surface-mid text-sm text-center py-8"
        >
          No tasks found.
        </p>
      </div>
    </div>

    <!-- Sync queue -->
    <div v-if="activeTab === 'sync'">
      <div class="space-y-3">
        <BaseCard v-for="item in syncQueue" :key="item.id" hoverable>
          <div class="flex justify-between items-start">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-surface-light font-bold text-sm">
                  Task #{{ item.task_id }}
                </span>
                <span class="text-xs text-accent-blue">
                  {{ item.action }}
                </span>
                <span
                  :class="[
                    'text-[10px] px-2 py-0.5 rounded-full border',
                    statusColors[item.status] ?? 'text-surface-mid',
                  ]"
                >
                  {{ item.status }}
                </span>
              </div>
              <div class="text-xs text-surface-mid">
                Attempts: {{ item.attempts }}
                <span v-if="item.next_retry_at">
                  | Next retry: {{ formatDate(item.next_retry_at) }}
                </span>
              </div>
              <div
                v-if="item.last_error"
                class="text-xs text-red-400 mt-1 truncate"
              >
                {{ item.last_error }}
              </div>
            </div>
            <BaseButton
              v-if="item.status === 'failed'"
              variant="ghost"
              size="sm"
              @click="retrySync(item.task_id)"
            >
              Retry
            </BaseButton>
          </div>
        </BaseCard>

        <p
          v-if="syncQueue.length === 0"
          class="text-surface-mid text-sm text-center py-8"
        >
          Sync queue is empty.
        </p>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="showCreateForm"
          class="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4 bg-black/60"
          @click.self="showCreateForm = false"
        >
          <div class="bg-surface-card border border-surface-border rounded-lg p-6 w-full max-w-lg">
            <h2 class="text-lg font-bold text-surface-light mb-6">New task</h2>
            <form class="space-y-4" @submit.prevent="createTask">
              <BaseInput v-model="createForm.title" label="Title" placeholder="What needs doing?" />
              <BaseInput
                v-model="createForm.scheduled_at"
                label="Scheduled at"
                type="datetime-local"
              />
              <BaseInput
                v-model="createForm.location"
                label="Location"
                placeholder="Optional"
              />
              <div>
                <label class="text-sm text-surface-mid font-mono block mb-1">Notes</label>
                <textarea
                  v-model="createForm.description"
                  rows="3"
                  placeholder="Optional details"
                  class="w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
                         focus:outline-none focus:border-accent-blue transition-colors resize-none"
                />
              </div>
              <div class="flex gap-3 pt-2">
                <BaseButton variant="primary" :disabled="saving">
                  {{ saving ? "Creating..." : "Create" }}
                </BaseButton>
                <BaseButton variant="ghost" type="button" @click="showCreateForm = false">
                  Cancel
                </BaseButton>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Task detail drawer -->
    <Teleport to="body">
      <Transition name="fade">
        <div
          v-if="selectedTask"
          class="fixed inset-0 z-50 flex justify-end"
          @click.self="closeDetail"
        >
          <div
            class="absolute inset-0 bg-black/60 backdrop-blur-sm"
            @click="closeDetail"
          />
          <div
            class="relative w-full max-w-md bg-surface-dark border-l border-surface-border overflow-y-auto p-6"
          >
            <div class="flex justify-between items-start mb-6">
              <h2 class="text-lg font-bold text-surface-light">
                {{ selectedTask.title }}
              </h2>
              <button
                class="text-surface-mid hover:text-surface-light text-xl leading-none"
                @click="closeDetail"
              >
                &times;
              </button>
            </div>

            <div class="space-y-4">
              <div>
                <span
                  :class="[
                    'text-xs px-2 py-1 rounded-full border',
                    statusColors[selectedTask.status] ?? 'text-surface-mid',
                  ]"
                >
                  {{ selectedTask.status }}
                </span>
              </div>

              <div class="text-xs text-surface-mid space-y-1">
                <div>
                  Scheduled: {{ formatDate(selectedTask.scheduled_at) }}
                </div>
                <div v-if="selectedTask.location">
                  Location: {{ selectedTask.location }}
                </div>
                <div v-if="selectedTask.description">
                  Notes: {{ selectedTask.description }}
                </div>
                <div v-if="selectedTask.google_event_id">
                  Google Event: {{ selectedTask.google_event_id }}
                </div>
                <div>Created: {{ formatDate(selectedTask.created_at) }}</div>
              </div>

              <!-- Reminders -->
              <div v-if="selectedTask.reminders.length">
                <h3
                  class="text-sm font-bold text-surface-light mb-2 border-t border-surface-border pt-4"
                >
                  Reminders
                </h3>
                <div class="space-y-2">
                  <div
                    v-for="r in selectedTask.reminders"
                    :key="r.id"
                    class="text-xs text-surface-mid flex justify-between"
                  >
                    <span>{{ formatDate(r.remind_at) }}</span>
                    <span
                      :class="
                        r.sent ? 'text-green-400' : 'text-yellow-400'
                      "
                    >
                      {{ r.sent ? "sent" : "pending" }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Status history -->
              <div v-if="selectedTask.status_history.length">
                <h3
                  class="text-sm font-bold text-surface-light mb-2 border-t border-surface-border pt-4"
                >
                  Status history
                </h3>
                <div class="space-y-2">
                  <div
                    v-for="h in selectedTask.status_history"
                    :key="h.id"
                    class="text-xs text-surface-mid"
                  >
                    <span class="text-red-400">{{ h.old_status }}</span>
                    <span class="mx-1">&rarr;</span>
                    <span class="text-green-400">{{ h.new_status }}</span>
                    <span class="ml-2 opacity-60">
                      {{ formatDate(h.changed_at) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Retry sync -->
              <div class="border-t border-surface-border pt-4">
                <BaseButton
                  variant="ghost"
                  size="sm"
                  @click="retrySync(selectedTask.id)"
                >
                  Retry calendar sync
                </BaseButton>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </AdminPageLayout>
</template>
