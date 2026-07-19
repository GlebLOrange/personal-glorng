import { computed, ref, watch } from "vue";

import { useApiAction } from "@/composables/useApiAction";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { statusLabel, type TaskStatus } from "@/constants/taskStatus";
import { datetimeLocalValue, parseDatetimeLocalToIso } from "@/utils/dates";
import type {
  PaginatedList,
  SyncQueueItem,
  TaskDetail,
  TaskIntakeItem,
  TaskItem,
} from "@/types";

export interface TaskCreateForm {
  title: string;
  scheduled_at: string;
  description: string;
  location: string;
}

export function useTasks() {
  const tasks = ref<TaskItem[]>([]);
  const syncQueue = ref<SyncQueueItem[]>([]);
  const intakes = ref<TaskIntakeItem[]>([]);
  const selectedTask = ref<TaskDetail | null>(null);
  const filterStatus = ref("");
  const searchQuery = ref("");
  const page = ref(1);
  const intakePage = ref(1);
  const syncPage = ref(1);
  const totalPages = ref(0);
  const intakeTotalPages = ref(0);
  const syncTotalPages = ref(0);
  const total = ref(0);
  const intakeTotal = ref(0);
  const syncTotal = ref(0);
  const showCreateForm = ref(false);
  const createForm = ref<TaskCreateForm>({
    title: "",
    scheduled_at: "",
    description: "",
    location: "",
  });

  const { loading: listLoading, run: runList } = useApiAction();
  const { loading: intakesLoading, run: runIntakes } = useApiAction();
  const { loading: syncLoading, run: runSync } = useApiAction();
  const { loading: detailLoading, run: runDetail } = useApiAction();
  const { loading: saving, run: runSave } = useApiAction();
  const { loading: statusUpdating, run: runStatusUpdate } = useApiAction();
  const { run: runRetry } = useApiAction();
  const { toast } = useNotify();

  const hasNextPage = computed(() => page.value < totalPages.value);
  const hasPreviousPage = computed(() => page.value > 1);
  const hasNextIntakePage = computed(() => intakePage.value < intakeTotalPages.value);
  const hasPreviousIntakePage = computed(() => intakePage.value > 1);
  const hasNextSyncPage = computed(() => syncPage.value < syncTotalPages.value);
  const hasPreviousSyncPage = computed(() => syncPage.value > 1);

  async function loadTasks(): Promise<void> {
    const params: Record<string, string | number> = {
      page: page.value,
      per_page: ADMIN_LIST_PAGE_SIZE,
    };
    if (filterStatus.value) {
      params.status = filterStatus.value;
    }
    const q = searchQuery.value.trim();
    if (q) {
      params.q = q;
    }

    const data = await runList(
      async () => {
        const response = await api.get<PaginatedList<TaskItem>>("/tools/tasks", { params });
        return response.data;
      },
      { errorFallback: "Failed to load tasks" },
    );
    if (data) {
      tasks.value = data.items;
      totalPages.value = data.pages;
      total.value = data.total;
    }
  }

  async function loadIntakes(): Promise<void> {
    const data = await runIntakes(
      async () => {
        const response = await api.get<PaginatedList<TaskIntakeItem>>("/tools/tasks/intakes", {
          params: { page: intakePage.value, per_page: ADMIN_LIST_PAGE_SIZE },
        });
        return response.data;
      },
      { errorFallback: "Failed to load intakes" },
    );
    if (data) {
      intakes.value = data.items;
      intakeTotalPages.value = data.pages;
      intakeTotal.value = data.total;
    }
  }

  async function loadSyncQueue(): Promise<void> {
    const data = await runSync(
      async () => {
        const response = await api.get<PaginatedList<SyncQueueItem>>("/tools/tasks/sync-queue", {
          params: { page: syncPage.value, per_page: ADMIN_LIST_PAGE_SIZE },
        });
        return response.data;
      },
      { errorFallback: "Failed to load sync queue" },
    );
    if (data) {
      syncQueue.value = data.items;
      syncTotalPages.value = data.pages;
      syncTotal.value = data.total;
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
    await loadTasks();
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
      await loadTasks();
    }
  }

  function goToPage(nextPage: number): void {
    if (nextPage < 1) return;
    if (totalPages.value > 0 && nextPage > totalPages.value) return;
    page.value = nextPage;
  }

  function goToIntakePage(nextPage: number): void {
    if (nextPage < 1) return;
    if (intakeTotalPages.value > 0 && nextPage > intakeTotalPages.value) return;
    intakePage.value = nextPage;
  }

  function goToSyncPage(nextPage: number): void {
    if (nextPage < 1) return;
    if (syncTotalPages.value > 0 && nextPage > syncTotalPages.value) return;
    syncPage.value = nextPage;
  }

  watch(filterStatus, () => {
    page.value = 1;
    void loadTasks();
  });

  let searchDebounce: ReturnType<typeof setTimeout> | undefined;
  watch(searchQuery, () => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => {
      page.value = 1;
      void loadTasks();
    }, 300);
  });

  watch(page, () => {
    void loadTasks();
  });

  watch(intakePage, () => {
    void loadIntakes();
  });

  watch(syncPage, () => {
    void loadSyncQueue();
  });

  return {
    tasks,
    syncQueue,
    intakes,
    selectedTask,
    filterStatus,
    searchQuery,
    page,
    intakePage,
    syncPage,
    totalPages,
    intakeTotalPages,
    syncTotalPages,
    total,
    intakeTotal,
    syncTotal,
    showCreateForm,
    createForm,
    listLoading,
    intakesLoading,
    syncLoading,
    detailLoading,
    saving,
    statusUpdating,
    hasNextPage,
    hasPreviousPage,
    hasNextIntakePage,
    hasPreviousIntakePage,
    hasNextSyncPage,
    hasPreviousSyncPage,
    loadTasks,
    loadIntakes,
    loadSyncQueue,
    openDetail,
    closeDetail,
    retrySync,
    updateTaskStatus,
    openCreate,
    createTask,
    goToPage,
    goToIntakePage,
    goToSyncPage,
  };
}
