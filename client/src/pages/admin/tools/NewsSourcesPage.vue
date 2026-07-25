<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminTabBar, { type AdminTab } from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import NewsSourceDrawer from "@/components/news/NewsSourceDrawer.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";
import { newsSourceEnabledClass } from "@/constants/filterColors";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import type { NewsSource, PaginatedList } from "@/types";
import { formatDate } from "@/utils/format";
import { normalizeHttpUrl, sourceFromUrl } from "@/utils/newsForms";

const SOURCES_API = "/tools/news/sources";

interface NewsSourceForm {
  name: string;
  feed_url: string;
  category: string;
  region: string;
  enabled: boolean;
}

interface MessageResponse {
  message: string;
}

type DrawerMode = "create" | "edit";
type EnabledFilter = "" | "enabled" | "disabled";

const ENABLED_FILTERS: { label: string; value: Exclude<EnabledFilter, ""> }[] = [
  { label: "enabled", value: "enabled" },
  { label: "disabled", value: "disabled" },
];

const blankForm = (): NewsSourceForm => ({
  name: "",
  feed_url: "",
  category: "world",
  region: "global",
  enabled: true,
});

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

const surfaceTabs = computed((): AdminTab[] => {
  const items: AdminTab[] = [{ id: "digest", label: "digest", family: "1xx" }];
  if (can("news", "read")) {
    items.push({ id: "manage", label: "manage", family: "1xx" });
  }
  return items;
});

/** Neither digest nor manage is selected while on this page. */
const surfaceTab = computed({
  get: () => "sources",
  set: (id: string) => {
    void onSurfaceTab(id);
  },
});

async function onSurfaceTab(id: string): Promise<void> {
  if (id === "manage") {
    await router.push({ name: "news", query: { manage: "1" } });
    return;
  }
  await router.push({ name: "news", query: {} });
}

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

async function deleteSource(source: NewsSource, event?: Event): Promise<void> {
  event?.stopPropagation();
  if (!canWrite.value) return;
  if (!window.confirm(`Delete ${source.name}?`)) return;
  deletingId.value = source.id;
  const ok = await runDelete(
    async () => {
      await api.delete(`${SOURCES_API}/${source.id}`);
      return true;
    },
    {
      successMessage: "News source deleted",
      errorMessage: "Failed to delete news source",
      logContext: "news.sources.delete",
    },
  );
  deletingId.value = null;
  if (!ok) return;
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
</script>

<template>
  <AdminPageLayout hub="tools" title="news sources" max-width="xl" back-to="/news">
    <div class="mb-3 flex min-w-0 flex-wrap items-center gap-2">
      <AdminFilterDropdown
        ref="filterDropdown"
        :has-active-filters="hasActiveFilters"
        :active-label="activeFilterLabel"
        @clear="clearFilters"
      >
        <template #chips>
          <AdminFilterChip
            v-for="chip in ENABLED_FILTERS"
            :key="chip.value"
            :label="chip.label"
            :active="enabledFilter === chip.value"
            :color-class="newsSourceEnabledClass(chip.value === 'enabled')"
            :disabled="loading"
            @click="setEnabledFilter(chip.value)"
          />
        </template>
      </AdminFilterDropdown>

      <AdminTabBar
        v-if="surfaceTabs.length > 0"
        v-model="surfaceTab"
        flush
        panel-id-prefix="news-sources-surface"
        :tabs="surfaceTabs"
      />

      <template v-if="canWrite">
        <ToolbarPillButton
          family="3xx"
          class="ml-auto"
          :disabled="refreshing || loading"
          @click="refreshSources"
        >
          {{ refreshButtonText }}
        </ToolbarPillButton>
        <ToolbarPillButton family="2xx" :disabled="loading" @click="openCreate">
          + source
        </ToolbarPillButton>
      </template>
    </div>

    <div class="min-w-0 divide-y divide-surface-border/40">
      <AdminListSkeleton v-if="loading" label="Loading sources" />

      <Card v-else-if="loadError" role="alert">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-sm text-accent-golden">News sources could not be loaded.</p>
          <BaseButton variant="ghost" size="sm" @click="loadSources">retry</BaseButton>
        </div>
      </Card>

      <template v-else>
        <EmptyState v-if="sources.length === 0" :description="emptyFilterDescription" />

        <template v-else>
          <AdminListRow
            v-for="source in sources"
            :key="source.id"
            :interactive="canWrite"
            :nested-interactive="canWrite"
            reveal-actions-on-hover
            @click="openEditableSource(source)"
          >
            <template #leading>
              <input
                v-if="canWrite"
                v-model="selectedSourceIds"
                type="checkbox"
                class="size-4 accent-accent-blue"
                :value="source.id"
                :disabled="refreshing || !source.enabled"
                :aria-label="`Select ${source.name} for parser refresh`"
                @click.stop
                @keydown.stop
              />
            </template>
            <template #badge>
              <StatusBadge
                :label="source.enabled ? 'enabled' : 'disabled'"
                :class-name="newsSourceEnabledClass(source.enabled)"
              />
            </template>
            <template #primary>
              <span :title="source.name">{{ source.name }}</span>
            </template>
            <template v-if="source.last_fetched_at" #meta>
              <span>{{ sourceMeta(source) }}</span>
            </template>
            <template #actions>
              <span
                v-if="source.last_error"
                class="text-xs text-accent-golden"
                :title="source.last_error"
                aria-label="Source has fetch error"
              >
                ⚠
              </span>
              <BaseButton
                v-if="canWrite"
                variant="ghost"
                quiet
                size="sm"
                class="!text-accent-blue hover:enabled:!bg-accent-blue/15 focus-visible:!text-accent-blue"
                aria-label="edit source"
                @click="openEditableSource(source)"
              >
                ✎
              </BaseButton>
              <IconCloseButton
                v-if="canWrite"
                aria-label="Delete source"
                :disabled="deletingId === source.id"
                @click="deleteSource(source, $event)"
              />
            </template>
          </AdminListRow>
        </template>

        <AdminListFooter
          :total="total"
          :page="page"
          :total-pages="totalPages"
          :has-next-page="hasNextPage"
          :has-previous-page="hasPreviousPage"
          :loading="loading"
          item-label="sources"
          ariaLabel="News sources pagination"
          @first="goToPage(1)"
          @prev="goToPage(page - 1)"
          @next="goToPage(page + 1)"
          @last="goToPage(totalPages)"
        />
      </template>
    </div>

    <NewsSourceDrawer
      v-if="canWrite"
      :open="drawerOpen"
      :mode="drawerMode"
      :form="form"
      :loading="saving"
      @update:form="updateForm"
      @close="closeDrawer"
      @save="saveSource"
    />
  </AdminPageLayout>
</template>
