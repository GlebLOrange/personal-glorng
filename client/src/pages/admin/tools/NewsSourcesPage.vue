<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import NewsSourceDrawer from "@/components/news/NewsSourceDrawer.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { Card } from "@/components/ui/card";
import { newsSourceEnabledClass } from "@/constants/filterColors";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import type { NewsSource, PaginatedList } from "@/types";
import { getApiErrorMessage } from "@/types/api";
import { formatDate } from "@/utils/format";
import { normalizeHttpUrl, sourceFromUrl } from "@/utils/newsForms";

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
const loading = ref(true);
const loadError = ref(false);
const saving = ref(false);
const refreshing = ref(false);
const deletingId = ref<number | null>(null);
const lastAutoName = ref<string | null>(null);
const { toast } = useNotify();
const { can } = usePermissions();
const canWrite = computed(() => can("news-sources", "write"));
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
  const parts = [source.category, source.region];
  if (source.last_fetched_at) {
    parts.push(`fetched ${formatDate(source.last_fetched_at)}`);
  }
  return parts.join(" · ");
}

async function loadSources(): Promise<void> {
  loading.value = true;
  loadError.value = false;
  try {
    const params: Record<string, string | number | boolean> = {
      page: page.value,
      per_page: ADMIN_LIST_PAGE_SIZE,
    };
    const enabled = enabledQueryParam();
    if (enabled !== undefined) params.enabled = enabled;
    const { data } = await api.get<PaginatedList<NewsSource>>("/tools/news-sources", {
      params,
    });
    sources.value = data.items;
    total.value = data.total;
    totalPages.value = data.pages;
    selectedSourceIds.value = selectedSourceIds.value.filter((id) =>
      data.items.some((source) => source.id === id && source.enabled),
    );
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    loadError.value = true;
    toast("Failed to load news sources", "error");
  } finally {
    loading.value = false;
  }
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
}

function openEdit(source: NewsSource): void {
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
  saving.value = true;
  try {
    const requestPayload = payload();
    if (!requestPayload) return;
    if (editingId.value) {
      await api.put(`/tools/news-sources/${editingId.value}`, requestPayload);
      toast("News source updated", "success");
    } else {
      await api.post("/tools/news-sources", requestPayload);
      toast("News source created", "success");
    }
    closeDrawer();
    await loadSources();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast(getApiErrorMessage(err, "Failed to save news source"), "error");
  } finally {
    saving.value = false;
  }
}

async function refreshSources(): Promise<void> {
  if (!canWrite.value) return;
  refreshing.value = true;
  try {
    const { data } = await api.post<MessageResponse>("/tools/news-sources/refresh", {
      source_ids: selectedSourceIds.value.length ? selectedSourceIds.value : null,
    });
    toast(data.message, "success");
    await loadSources();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to queue news parser", "error");
  } finally {
    refreshing.value = false;
  }
}

async function deleteSource(source: NewsSource, event?: Event): Promise<void> {
  event?.stopPropagation();
  if (!canWrite.value) return;
  if (!window.confirm(`Delete ${source.name}?`)) return;
  deletingId.value = source.id;
  try {
    await api.delete(`/tools/news-sources/${source.id}`);
    sources.value = sources.value.filter((item) => item.id !== source.id);
    if (editingId.value === source.id) closeDrawer();
    toast("News source deleted", "success");
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast(getApiErrorMessage(err, "Failed to delete news source"), "error");
  } finally {
    deletingId.value = null;
  }
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

onMounted(loadSources);
</script>

<template>
  <AdminPageLayout hub="tools" title="news sources" max-width="xl">
    <div class="min-w-0 space-y-1">
      <AdminListSkeleton v-if="loading" label="Loading sources" />

      <Card v-else-if="loadError" role="alert">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-sm text-accent-golden">News sources could not be loaded.</p>
          <BaseButton variant="ghost" size="sm" @click="loadSources">retry</BaseButton>
        </div>
      </Card>

      <template v-else>
        <AdminListToolbar>
          <template #start>
            <div class="flex w-full min-w-0 flex-wrap items-center gap-3">
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
                    @click="setEnabledFilter(chip.value)"
                  />
                </template>
              </AdminFilterDropdown>
              <div v-if="canWrite" class="ml-auto flex shrink-0 flex-wrap items-center gap-2">
                <BaseButton
                  variant="ghost"
                  size="sm"
                  :disabled="refreshing"
                  @click="refreshSources"
                >
                  {{ refreshButtonText }}
                </BaseButton>
                <BaseButton
                  variant="primary"
                  size="sm"
                  @click="openCreate"
                >
                  add source
                </BaseButton>
              </div>
            </div>
          </template>
        </AdminListToolbar>

        <EmptyState v-if="sources.length === 0" :description="emptyFilterDescription" />

        <template v-else>
          <AdminListRow
          v-for="source in sources"
          :key="source.id"
          :interactive="canWrite"
          :nested-interactive="canWrite"
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
          <template #meta>
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
            <button
              v-if="canWrite"
              type="button"
              class="rounded-lg border border-transparent bg-transparent px-3 py-1.5 text-xs font-medium text-status-error transition-colors hover:border-status-error/40 hover:bg-status-error/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-status-error/50 disabled:cursor-not-allowed disabled:opacity-50"
              aria-label="Delete source"
              :disabled="deletingId === source.id"
              @click="deleteSource(source, $event)"
            >
              ✕
            </button>
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
