import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { usePermissions } from "@/composables/usePermissions";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import type { HealthHistoryPoint, HealthMonitor, PaginatedList } from "@/types";
import { ensureHttpsUrl } from "@/utils/ensureHttpsUrl";

export type HealthInterval = 1 | 5 | 15 | 60;

export const HEALTH_INTERVALS: HealthInterval[] = [1, 5, 15, 60];

export function useHealthChecker() {
  const { can } = usePermissions();
  const canRead = computed(() => can("health-checker", "read"));
  const canWrite = computed(() => can("health-checker", "write"));

  const monitors = ref<HealthMonitor[]>([]);
  const page = ref(1);
  const total = ref(0);
  const totalPages = ref(0);
  const selectedId = ref<number | null>(null);
  const history = ref<HealthHistoryPoint[]>([]);

  const newUrl = ref("");
  const newLabel = ref("");
  const newInterval = ref<HealthInterval>(5);

  const { loading: listLoading, run: runList } = useApiAction();
  const { loading: creating, run: runCreate } = useApiAction();
  const { loading: checking, run: runCheck } = useApiAction();
  const { loading: historyLoading, run: runHistory } = useApiAction();
  const { run: runUpdate } = useApiAction();
  const { run: runDelete } = useApiAction();

  const selected = computed(
    () => monitors.value.find((m) => m.id === selectedId.value) ?? null,
  );

  const chartLabels = computed(() =>
    history.value.map((p) => {
      const d = new Date(p.checked_at);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }),
  );

  const chartValues = computed(() =>
    history.value.map((p) => (p.response_ms == null ? 0 : p.response_ms)),
  );

  async function loadMonitors(): Promise<void> {
    if (!canRead.value) return;
    const data = await runList(
      () =>
        api.get<PaginatedList<HealthMonitor>>("/tools/health-checker", {
          params: { page: page.value, per_page: ADMIN_LIST_PAGE_SIZE },
        }),
      { errorFallback: "Failed to load monitors" },
    );
    if (data) {
      monitors.value = data.data.items;
      total.value = data.data.total;
      totalPages.value = data.data.pages;
      if (
        selectedId.value != null &&
        !monitors.value.some((m) => m.id === selectedId.value)
      ) {
        selectedId.value = null;
        history.value = [];
      }
    }
  }

  async function loadHistory(monitorId: number): Promise<void> {
    const data = await runHistory(
      () =>
        api.get<{ items: HealthHistoryPoint[] }>(
          `/tools/health-checker/${monitorId}/history`,
          { params: { hours: 24 } },
        ),
      { errorFallback: "Failed to load history" },
    );
    if (data) {
      history.value = data.data.items;
    }
  }

  async function selectMonitor(id: number): Promise<void> {
    selectedId.value = id;
    await loadHistory(id);
  }

  async function createMonitor(): Promise<void> {
    if (!newUrl.value.trim() || !canWrite.value) return;
    const result = await runCreate(
      () =>
        api.post<HealthMonitor>("/tools/health-checker", {
          url: ensureHttpsUrl(newUrl.value),
          label: newLabel.value.trim() || null,
          interval_minutes: newInterval.value,
        }),
      {
        successMessage: "Monitor created",
        errorFallback: "Failed to create monitor",
      },
    );
    if (result) {
      newUrl.value = "";
      newLabel.value = "";
      newInterval.value = 5;
      page.value = 1;
      await loadMonitors();
      selectedId.value = result.data.id;
      await loadHistory(result.data.id);
    }
  }

  async function checkNow(id: number): Promise<void> {
    const result = await runCheck(
      () => api.post<HealthMonitor>(`/tools/health-checker/${id}/check`),
      {
        successMessage: "Check complete",
        errorFallback: "Check failed",
      },
    );
    if (result) {
      const idx = monitors.value.findIndex((m) => m.id === id);
      if (idx !== -1) {
        monitors.value[idx] = result.data;
      }
      if (selectedId.value === id) {
        await loadHistory(id);
      }
    }
  }

  async function toggleEnabled(monitor: HealthMonitor): Promise<void> {
    const result = await runUpdate(
      () =>
        api.patch<HealthMonitor>(`/tools/health-checker/${monitor.id}`, {
          enabled: !monitor.enabled,
        }),
      {
        successMessage: monitor.enabled ? "Paused" : "Resumed",
        errorFallback: "Failed to update monitor",
      },
    );
    if (result) {
      const idx = monitors.value.findIndex((m) => m.id === monitor.id);
      if (idx !== -1) {
        monitors.value[idx] = result.data;
      }
    }
  }

  async function updateInterval(
    monitor: HealthMonitor,
    interval: HealthInterval,
  ): Promise<void> {
    const result = await runUpdate(
      () =>
        api.patch<HealthMonitor>(`/tools/health-checker/${monitor.id}`, {
          interval_minutes: interval,
        }),
      {
        successMessage: "Interval updated",
        errorFallback: "Failed to update interval",
      },
    );
    if (result) {
      const idx = monitors.value.findIndex((m) => m.id === monitor.id);
      if (idx !== -1) {
        monitors.value[idx] = result.data;
      }
    }
  }

  async function deleteMonitor(id: number): Promise<void> {
    const result = await runDelete(() => api.delete(`/tools/health-checker/${id}`), {
      successMessage: "Monitor deleted",
      errorFallback: "Failed to delete monitor",
    });
    if (result) {
      if (selectedId.value === id) {
        selectedId.value = null;
        history.value = [];
      }
      await loadMonitors();
    }
  }

  function goToPage(nextPage: number): void {
    if (nextPage < 1) return;
    if (totalPages.value > 0 && nextPage > totalPages.value) return;
    page.value = nextPage;
    void loadMonitors();
  }

  return {
    canRead,
    canWrite,
    monitors,
    page,
    total,
    totalPages,
    selectedId,
    selected,
    history,
    chartLabels,
    chartValues,
    newUrl,
    newLabel,
    newInterval,
    listLoading,
    creating,
    checking,
    historyLoading,
    loadMonitors,
    selectMonitor,
    createMonitor,
    checkNow,
    toggleEnabled,
    updateInterval,
    deleteMonitor,
    goToPage,
  };
}
