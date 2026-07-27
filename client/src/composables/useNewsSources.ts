import { computed, onMounted, ref, useTemplateRef, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import type { NewsSource, PaginatedList } from "@/types";
import { formatDate } from "@/utils/format";
import { normalizeHttpUrl, sourceFromUrl } from "@/utils/newsForms";

const SOURCES_API = "/tools/news/sources";

export interface NewsSourceForm {
  name: string;
  feed_url: string;
  category: string;
  region: string;
  enabled: boolean;
}

interface MessageResponse {
  message: string;
}

export type DrawerMode = "create" | "edit";
export type EnabledFilter = "" | "enabled" | "disabled";

export const ENABLED_FILTERS: { label: string; value: Exclude<EnabledFilter, ""> }[] = [
  { label: "enabled", value: "enabled" },
  { label: "disabled", value: "disabled" },
];

export function blankForm(): NewsSourceForm {
  return {
    name: "",
    feed_url: "",
    category: "world",
    region: "global",
    enabled: true,
  };
}

/** News sources admin list + drawer orchestration. */
export function useNewsSources() {
  const route = useRoute();
  const router = useRouter();
  const sources = ref<NewsSource[]>([]);
  const page = ref(1);
  const enabledFilter = ref<EnabledFilter>("");
  const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");
  const total = ref(0);
  const totalPages = ref(0);
  const selectedSourceIds = ref<number[]>([]);
  const form = ref<NewsSourceForm>(blankForm());
  const drawerOpen = ref(false);
  const drawerMode = ref<DrawerMode>("create");
  const editingId = ref<number | null>(null);
  const { loading, lastError: listError, run: runLoad } = useApiAction({ silent: true });
  const { run: runSave, loading: saving } = useApiAction();
  const { run: runRefresh, loading: refreshing } = useApiAction();
  const { run: runDelete } = useApiAction();
  const deletingId = ref<number | null>(null);
  const showDeleteConfirm = ref(false);
  const pendingDeleteSource = ref<NewsSource | null>(null);
  const deleteConfirmMessage = computed(() => {
    const name = pendingDeleteSource.value?.name?.trim();
    return name ? `delete ${name}?` : "delete this news source?";
  });

  const lastAutoName = ref<string | null>(null);
  const { toast } = useNotify();
  const { can } = usePermissions();
  const canWrite = computed(() => can("news-sources", "write"));
  const loadError = computed(() => listError.value !== null);
  // ponytail: show skeleton before first onMounted load (useApiAction starts false)
  loading.value = true;
  const selectedSourceCount = computed(() => selectedSourceIds.value.length);
  const refreshButtonText = computed(() => {
    if (refreshing.value) return "queueing...";
    if (selectedSourceCount.value) return `queue parser (${selectedSourceCount.value})`;
    return "queue parser";
  });

  const hasNextPage = computed(() => page.value < totalPages.value);
  const hasPreviousPage = computed(() => page.value > 1);
  const hasActiveFilters = computed(() => Boolean(enabledFilter.value));
  const activeFilterLabel = computed(
    () => ENABLED_FILTERS.find((chip) => chip.value === enabledFilter.value)?.label,
  );

  const emptyFilterDescription = computed(() => {
    if (enabledFilter.value === "enabled") return "No enabled news sources.";
    if (enabledFilter.value === "disabled") return "No disabled news sources.";
    return "No news sources yet.";
  });

  const routeSourceId = computed(() => {
    const raw = route.params.id;
    if (typeof raw !== "string") return null;
    const id = Number(raw);
    return Number.isFinite(id) ? id : null;
  });

  function enabledQueryParam(): boolean | undefined {
    if (enabledFilter.value === "enabled") return true;
    if (enabledFilter.value === "disabled") return false;
    return undefined;
  }

  function setEnabledFilter(next: Exclude<EnabledFilter, "">): void {
    enabledFilter.value = next;
    page.value = 1;
    filterDropdownRef.value?.close();
    void loadSources();
  }

  function clearFilters(): void {
    enabledFilter.value = "";
    page.value = 1;
    filterDropdownRef.value?.close();
    void loadSources();
  }

  function sourceMeta(source: NewsSource): string {
    if (!source.last_fetched_at) return "";
    return `fetched ${formatDate(source.last_fetched_at)}`;
  }

  function syncRouteSource(): void {
    const id = routeSourceId.value;
    if (id == null) return;
    const source = sources.value.find((item) => item.id === id);
    if (source) {
      openEdit(source, false);
      return;
    }
    void router.replace({ name: "news-sources" });
  }

  async function loadSources(): Promise<void> {
    const data = await runLoad(
      async () => {
        const params: Record<string, string | number | boolean> = {
          page: page.value,
          per_page: ADMIN_LIST_PAGE_SIZE,
        };
        const enabled = enabledQueryParam();
        if (enabled !== undefined) params.enabled = enabled;
        const response = await api.get<PaginatedList<NewsSource>>(SOURCES_API, {
          params,
        });
        return response.data;
      },
      { errorFallback: "Failed to load news sources", logContext: "news.sources.load" },
    );
    if (!data) return;
    sources.value = data.items;
    total.value = data.total;
    totalPages.value = data.pages;
    selectedSourceIds.value = selectedSourceIds.value.filter((id) =>
      data.items.some((source) => source.id === id && source.enabled),
    );
    syncRouteSource();
  }

  function goToPage(nextPage: number): void {
    if (nextPage < 1) return;
    if (totalPages.value > 0 && nextPage > totalPages.value) return;
    page.value = nextPage;
    void loadSources();
  }

  function openCreate(): void {
    drawerMode.value = "create";
    editingId.value = null;
    lastAutoName.value = null;
    form.value = blankForm();
    drawerOpen.value = true;
    if (routeSourceId.value != null) {
      void router.replace({ name: "news-sources" });
    }
  }

  function openEdit(source: NewsSource, syncRoute = true): void {
    drawerMode.value = "edit";
    editingId.value = source.id;
    lastAutoName.value = null;
    form.value = {
      name: source.name,
      feed_url: source.feed_url,
      category: source.category,
      region: source.region,
      enabled: source.enabled,
    };
    drawerOpen.value = true;
    if (syncRoute && routeSourceId.value !== source.id) {
      void router.replace({ name: "news-source", params: { id: String(source.id) } });
    }
  }

  function openEditableSource(source: NewsSource): void {
    if (!canWrite.value) return;
    openEdit(source);
  }

  function closeDrawer(): void {
    drawerOpen.value = false;
    editingId.value = null;
    lastAutoName.value = null;
    form.value = blankForm();
    if (routeSourceId.value != null) {
      void router.replace({ name: "news-sources" });
    }
  }

  function updateForm(nextForm: NewsSourceForm): void {
    form.value = nextForm;
  }

  function payload(): Record<string, string | boolean | null> | null {
    const feedUrl = normalizeHttpUrl(form.value.feed_url);
    if (!feedUrl) {
      toast("Enter a valid http(s) feed URL", "error");
      return null;
    }
    return {
      name: form.value.name.trim(),
      feed_url: feedUrl,
      category: form.value.category.trim(),
      region: form.value.region.trim(),
      enabled: form.value.enabled,
    };
  }

  async function saveSource(): Promise<void> {
    if (!canWrite.value) return;
    const requestPayload = payload();
    if (!requestPayload) return;
    const editing = editingId.value;
    const ok = await runSave(
      async () => {
        if (editing) {
          await api.put(`${SOURCES_API}/${editing}`, requestPayload);
        } else {
          await api.post(SOURCES_API, requestPayload);
        }
        return true;
      },
      {
        successMessage: editing ? "News source updated" : "News source created",
        errorMessage: "Failed to save news source",
        logContext: "news.sources.save",
      },
    );
    if (!ok) return;
    closeDrawer();
    await loadSources();
  }

  async function refreshSources(): Promise<void> {
    if (!canWrite.value) return;
    const data = await runRefresh(
      async () => {
        const response = await api.post<MessageResponse>(`${SOURCES_API}/refresh`, {
          source_ids: selectedSourceIds.value.length ? selectedSourceIds.value : null,
        });
        return response.data;
      },
      { errorMessage: "Failed to queue news parser", logContext: "news.sources.refresh" },
    );
    if (!data) return;
    toast(data.message, "success");
    await loadSources();
  }

  function requestDeleteSource(source: NewsSource, event?: Event): void {
    event?.stopPropagation();
    if (!canWrite.value) return;
    pendingDeleteSource.value = source;
    showDeleteConfirm.value = true;
  }

  function cancelDeleteSource(): void {
    showDeleteConfirm.value = false;
    pendingDeleteSource.value = null;
  }

  async function confirmDeleteSource(): Promise<void> {
    const source = pendingDeleteSource.value;
    if (!source || !canWrite.value) return;
    deletingId.value = source.id;
    const ok = await runDelete(
      async () => {
        await api.delete(`${SOURCES_API}/${source.id}`);
        return true;
      },
      {
        successMessage: "news source deleted",
        errorMessage: "failed to delete news source",
        logContext: "news.sources.delete",
      },
    );
    deletingId.value = null;
    if (!ok) return;
    showDeleteConfirm.value = false;
    pendingDeleteSource.value = null;
    sources.value = sources.value.filter((item) => item.id !== source.id);
    if (editingId.value === source.id) closeDrawer();
  }

  watch(
    () => form.value.feed_url,
    (feedUrl) => {
      if (editingId.value) return;
      const source = sourceFromUrl(feedUrl);
      if (!source) return;
      const currentName = form.value.name.trim();
      if (currentName && currentName !== lastAutoName.value) return;
      form.value.name = source;
      lastAutoName.value = source;
    },
  );

  watch(routeSourceId, () => {
    if (!loading.value) syncRouteSource();
  });

  onMounted(loadSources);

  return {
    sources,
    page,
    enabledFilter,
    total,
    totalPages,
    selectedSourceIds,
    form,
    drawerOpen,
    drawerMode,
    editingId,
    loading,
    saving,
    refreshing,
    deletingId,
    showDeleteConfirm,
    deleteConfirmMessage,
    canWrite,
    loadError,
    refreshButtonText,
    hasNextPage,
    hasPreviousPage,
    hasActiveFilters,
    activeFilterLabel,
    emptyFilterDescription,
    setEnabledFilter,
    clearFilters,
    sourceMeta,
    loadSources,
    goToPage,
    openCreate,
    openEditableSource,
    closeDrawer,
    updateForm,
    saveSource,
    refreshSources,
    requestDeleteSource,
    confirmDeleteSource,
    cancelDeleteSource,
  };
}
