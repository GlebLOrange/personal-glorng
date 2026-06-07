import { computed, ref, watch } from "vue";

import { useApiAction } from "@/composables/useApiAction";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { statusLabel, type TaskStatus } from "@/constants/taskStatus";
import { datetimeLocalValue, parseDatetimeLocalToIso } from "@/utils/dates";
import type { SyncQueueItem, TaskDetail, TaskIntakeItem, TaskItem, TaskStats } from "@/types";

const PER_PAGE = 20;

export interface TaskCreateForm {
  title: string;
  scheduled_at: string;
  description: string;
  location: string;
}

export function useTasks() {
  const tasks = ref<TaskItem[]>([]);
  const stats = ref<TaskStats | null>(null);
  const syncQueue = ref<SyncQueueItem[]>([]);
  const intakes = ref<TaskIntakeItem[]>([]);
  const selectedTask = ref<TaskDetail | null>(null);
  const filterStatus = ref("");
  const page = ref(1);
  const showCreateForm = ref(false);
  const createForm = ref<TaskCreateForm>({
    title: "",
    scheduled_at: "",
    description: "",
    location: "",
  });

  const { loading: listLoading, run: runList } = useApiAction();
  const { loading: statsLoading, run: runStats } = useApiAction();
  const { loading: intakesLoading, run: runIntakes } = useApiAction();
  const { loading: syncLoading, run: runSync } = useApiAction();
  const { loading: detailLoading, run: runDetail } = useApiAction();
  const { loading: saving, run: runSave } = useApiAction();
  const { loading: statusUpdating, run: runStatusUpdate } = useApiAction();
  const { run: runRetry } = useApiAction();
  const { toast } = useNotify();

  const hasNextPage = computed(() => tasks.value.length >= PER_PAGE);
  const taskCountLabel = computed(() => {
    const n = tasks.value.length;
    const filter = filterStatus.value ? ` · ${filterStatus.value.replaceAll("_", " ")}` : "";
    return `${n} task${n === 1 ? "" : "s"} on page ${page.value}${filter}`;
  });

  async function loadTasks(): Promise<void> {
    const params: Record<string, string | number> = {
      page: page.value,
      per_page: PER_PAGE,
    };
    if (filterStatus.value) {
      params.status = filterStatus.value;
    }

    const data = await runList(
      async () => {
        const response = await api.get<TaskItem[]>("/tools/tasks", { params });
        return response.data;
      },
      { errorFallback: "Failed to load tasks" },
    );
    if (data) {
      tasks.value = data;
    }
  }

  async function loadStats(): Promise<void> {
    const data = await runStats(
      async () => {
        const response = await api.get<TaskStats>("/tools/tasks/stats");
        return response.data;
      },
      { errorFallback: "Failed to load stats", silent: true },
    );
    if (data) {
      stats.value = data;
    }
  }

  async function loadIntakes(): Promise<void> {
    const data = await runIntakes(
      async () => {
        const response = await api.get<TaskIntakeItem[]>("/tools/tasks/intakes");
        return response.data;
      },
      { errorFallback: "Failed to load intakes" },
    );
    if (data) {
      intakes.value = data;
    }
  }

  async function loadSyncQueue(): Promise<void> {
    const data = await runSync(
      async () => {
        const response = await api.get<SyncQueueItem[]>("/tools/tasks/sync-queue");
        return response.data;
      },
      { errorFallback: "Failed to load sync queue" },
    );
    if (data) {
      syncQueue.value = data;
    }
  }

  async function openDetail(taskId: number): Promise<void> {
    const data = await runDetail(
      async () => {
        const response = await api.get<TaskDetail>(`/tools/tasks/${taskId}`);
        return response.data;
      },
      { errorFallback: "Failed to load task detail" },
    );
    if (data) {
      selectedTask.value = data;
    }
  }

  function closeDetail(): void {
    selectedTask.value = null;
  }

  async function retrySync(taskId: number): Promise<void> {
    await runRetry(
      async () => {
        await api.post(`/tools/tasks/${taskId}/retry-sync`);
      },
      { successMessage: "Sync retry queued", errorFallback: "Failed to retry sync" },
    );
    await loadSyncQueue();
  }

  async function updateTaskStatus(taskId: number, status: TaskStatus): Promise<void> {
    const result = await runStatusUpdate(
      async () => {
        await api.patch(`/tools/tasks/${taskId}/status`, { status });
      },
      {
        successMessage: `Status set to ${statusLabel(status)}`,
        errorFallback: "Failed to update status",
      },
    );
    if (result === null) return;

    if (selectedTask.value?.id === taskId) {
      await openDetail(taskId);
    }
    await Promise.all([loadTasks(), loadStats()]);
  }

  function openCreate(): void {
    createForm.value = {
      title: "",
      scheduled_at: datetimeLocalValue(),
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
    const scheduledAt = parseDatetimeLocalToIso(createForm.value.scheduled_at);
    if (!scheduledAt) {
      toast("Scheduled time is invalid", "error");
      return;
    }

    const result = await runSave(
      async () => {
        await api.post("/tools/tasks", {
          title: createForm.value.title.trim(),
          scheduled_at: scheduledAt,
          description: createForm.value.description.trim() || null,
          location: createForm.value.location.trim() || null,
        });
      },
      { successMessage: "Task created", errorFallback: "Failed to create task" },
    );
    if (result !== null) {
      showCreateForm.value = false;
      page.value = 1;
      await Promise.all([loadTasks(), loadStats()]);
    }
  }

  function goToPage(nextPage: number): void {
    if (nextPage < 1) return;
    page.value = nextPage;
  }

  watch([filterStatus], () => {
    page.value = 1;
    void loadTasks();
  });

  watch(page, () => {
    void loadTasks();
  });

  return {
    tasks,
    stats,
    syncQueue,
    intakes,
    selectedTask,
    filterStatus,
    page,
    showCreateForm,
    createForm,
    listLoading,
    statsLoading,
    intakesLoading,
    syncLoading,
    detailLoading,
    saving,
    statusUpdating,
    hasNextPage,
    taskCountLabel,
    loadTasks,
    loadStats,
    loadIntakes,
    loadSyncQueue,
    openDetail,
    closeDetail,
    retrySync,
    updateTaskStatus,
    openCreate,
    createTask,
    goToPage,
  };
}
