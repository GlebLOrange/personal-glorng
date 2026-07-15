<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { formatDate } from "@/utils/format";

interface AppLogEntry {
  id: number;
  occurred_at: string;
  level: string;
  message: string;
  logger: string;
  context: Record<string, unknown> | null;
  error: string | null;
  error_type: string | null;
  traceback: string | null;
  request_id: string | null;
}

const items = ref<AppLogEntry[]>([]);
const total = ref(0);
const loading = ref(false);
const listError = ref<string | null>(null);
const level = ref("");
const requestId = ref("");
const message = ref("");
const page = ref(1);
const expandedEntryIds = ref<Set<number>>(new Set());
const totalPages = computed(() => Math.ceil(total.value / ADMIN_LIST_PAGE_SIZE));
const hasPreviousPage = computed(() => page.value > 1);
const hasNextPage = computed(() => page.value < totalPages.value);
const hasActiveFilters = computed(
  () => Boolean(level.value || requestId.value.trim() || message.value.trim()),
);

useScrollListFingerprint(
  () =>
    `${page.value}:${total.value}:${level.value}:${requestId.value}:${message.value}:${items.value[0]?.id ?? ""}`,
);

async function load(): Promise<void> {
  loading.value = true;
  listError.value = null;
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      per_page: ADMIN_LIST_PAGE_SIZE,
    };
    if (level.value) params.level = level.value;
    if (requestId.value.trim()) params.request_id = requestId.value.trim();
    if (message.value.trim()) params.message = message.value.trim();
    const { data } = await api.get<{ items: AppLogEntry[]; total: number }>("/tools/app-logs", {
      params,
    });
    items.value = data.items;
    total.value = data.total;
    expandedEntryIds.value = new Set();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    listError.value = "Failed to load app logs.";
  } finally {
    loading.value = false;
  }
}

function applyFilters(): void {
  page.value = 1;
  void load();
}

function clearFilters(): void {
  level.value = "";
  requestId.value = "";
  message.value = "";
  page.value = 1;
  void load();
}

function goToPage(nextPage: number): void {
  if (nextPage < 1 || (totalPages.value > 0 && nextPage > totalPages.value)) return;
  page.value = nextPage;
  void load();
}

function toggleExpanded(entryId: number): void {
  const next = new Set(expandedEntryIds.value);
  if (next.has(entryId)) {
    next.delete(entryId);
  } else {
    next.add(entryId);
  }
  expandedEntryIds.value = next;
}

function onRowClick(entry: AppLogEntry): void {
  if (hasDetails(entry)) toggleExpanded(entry.id);
}

function hasDetails(entry: AppLogEntry): boolean {
  return Boolean(entry.context || entry.traceback || entry.error || entry.request_id);
}

function levelClass(logLevel: string): string {
  switch (logLevel) {
    case "error":
      return "bg-accent-red/20 text-accent-red border-accent-red/30";
    case "warning":
      return "bg-accent-amber/20 text-accent-amber border-accent-amber/30";
    case "debug":
      return "bg-surface-border text-surface-mid border-surface-border";
    default:
      return "bg-accent-blue/20 text-accent-blue border-accent-blue/30";
  }
}

onMounted(load);
</script>

<template>
  <AdminPageLayout title="app logs">
    <header class="page-intro">
      <p class="text-xs text-surface-muted">
        Structured application logs persisted from the API server. Message search uses
        Elasticsearch when enabled.
      </p>
    </header>

    <AdminListSkeleton v-if="loading && items.length === 0 && !listError" label="Loading app logs" />

    <template v-else>
      <AdminListToolbar
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        :loading="loading"
        item-label="entries"
        ariaLabel="App logs pagination"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
      >
        <template #start>
          <AdminFilterDropdown
            :has-active-filters="hasActiveFilters"
            @apply="applyFilters"
            @clear="clearFilters"
          >
            <BaseSelect v-model="level" label="level" compact>
              <option value="">All</option>
              <option value="debug">debug</option>
              <option value="info">info</option>
              <option value="warning">warning</option>
              <option value="error">error</option>
            </BaseSelect>
            <BaseInput v-model="requestId" label="request id" compact placeholder="UUID" />
            <BaseInput v-model="message" label="message" compact placeholder="substring" />
          </AdminFilterDropdown>
        </template>
      </AdminListToolbar>

      <ErrorState v-if="listError" class="mt-4" :message="listError" show-retry @retry="load" />

      <EmptyState v-else-if="items.length === 0" class="mt-4" description="No log entries found." />

      <div v-else class="min-w-0 mt-1 space-y-1">
        <AdminListRow
          v-for="entry in items"
          :key="entry.id"
          :interactive="hasDetails(entry)"
          :expandable="hasDetails(entry)"
          :expanded="expandedEntryIds.has(entry.id)"
          :hoverable="hasDetails(entry)"
          @click="onRowClick(entry)"
        >
          <template #badge>
            <StatusBadge :label="entry.level" :class-name="levelClass(entry.level)" />
          </template>
          <template #primary>
            <span :title="entry.message">{{ entry.message }}</span>
          </template>
          <template #meta>
            <span class="font-data">{{ entry.logger }}</span>
          </template>
          <template #time>{{ formatDate(entry.occurred_at) }}</template>
          <template #detail>
            <p v-if="entry.request_id" class="font-data">Request: {{ entry.request_id }}</p>
            <p v-if="entry.error_type">Error: {{ entry.error_type }} — {{ entry.error }}</p>
            <pre
              v-if="entry.context"
              class="mt-2 overflow-x-auto rounded bg-surface-dark p-2 text-xs"
              >{{ JSON.stringify(entry.context, null, 2) }}</pre
            >
            <pre
              v-if="entry.traceback"
              class="mt-2 overflow-x-auto rounded bg-surface-dark p-2 text-xs text-accent-red/80"
              >{{ entry.traceback }}</pre
            >
          </template>
        </AdminListRow>
      </div>
    </template>
  </AdminPageLayout>
</template>
