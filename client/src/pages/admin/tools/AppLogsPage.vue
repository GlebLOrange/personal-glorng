<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BasePagination from "@/components/ui/BasePagination.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import { Card } from "@/components/ui/card";
import { LIST_PAGE_SIZE } from "@/constants/pagination";
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
const totalPages = computed(() => Math.ceil(total.value / LIST_PAGE_SIZE));
const hasPreviousPage = computed(() => page.value > 1);
const hasNextPage = computed(() => page.value < totalPages.value);

useScrollListFingerprint(
  () =>
    `${page.value}:${total.value}:${level.value}:${requestId.value}:${message.value}:${items.value[0]?.id ?? ""}`,
);

async function load(): Promise<void> {
  loading.value = true;
  listError.value = null;
  try {
    const params: Record<string, string | number> = { page: page.value, per_page: LIST_PAGE_SIZE };
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

function levelClass(logLevel: string): string {
  switch (logLevel) {
    case "error":
      return "bg-accent-red/20 text-accent-red";
    case "warning":
      return "bg-accent-amber/20 text-accent-amber";
    case "debug":
      return "bg-surface-border text-surface-mid";
    default:
      return "bg-accent-blue/20 text-accent-blue";
  }
}

onMounted(load);
</script>

<template>
  <AdminPageLayout title="app logs">
    <header class="page-intro">
      <p class="text-xs text-surface-muted">
        Structured application logs persisted from the API server
      </p>
    </header>

    <Card class="mb-6">
      <div class="flex flex-wrap gap-3 items-end">
        <BaseSelect v-model="level" label="Level" compact>
          <option value="">All</option>
          <option value="debug">debug</option>
          <option value="info">info</option>
          <option value="warning">warning</option>
          <option value="error">error</option>
        </BaseSelect>
        <BaseInput v-model="requestId" label="Request ID" compact placeholder="UUID" />
        <BaseInput v-model="message" label="Message" compact placeholder="substring" />
        <BaseButton size="sm" @click="applyFilters">Filter</BaseButton>
      </div>
    </Card>

    <section v-if="loading" class="space-y-3" aria-busy="true" aria-label="Loading app logs">
      <Card v-for="i in 5" :key="i" class="h-24 animate-pulse" />
    </section>

    <ErrorState
      v-else-if="listError"
      :message="listError"
      show-retry
      @retry="load"
    />

    <EmptyState v-else-if="items.length === 0" description="No log entries found." />

    <div v-else class="min-w-0 space-y-3">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <p class="text-xs text-surface-muted">
          {{ total }} entries total · page {{ page }} of {{ Math.max(totalPages, 1) }}
        </p>
        <BasePagination
          layout="compact"
          aria-label="App logs pagination"
          :page="page"
          :has-next-page="hasNextPage"
          :has-previous-page="hasPreviousPage"
          @prev="goToPage(page - 1)"
          @next="goToPage(page + 1)"
        />
      </div>
      <Card v-for="entry in items" :key="entry.id" class="text-sm">
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <span class="text-xs px-2 py-0.5 rounded" :class="levelClass(entry.level)">
            {{ entry.level }}
          </span>
          <span class="min-w-0 break-words text-surface-light">{{ entry.message }}</span>
          <span class="text-xs text-surface-muted ml-auto">
            {{ formatDate(entry.occurred_at) }}
          </span>
        </div>
        <div class="text-xs text-surface-mid space-y-1">
          <p>Logger: {{ entry.logger }}</p>
          <p v-if="entry.request_id" class="font-data text-xs">Request: {{ entry.request_id }}</p>
          <p v-if="entry.error_type">Error: {{ entry.error_type }} — {{ entry.error }}</p>
          <BaseButton
            v-if="entry.context || entry.traceback"
            size="sm"
            variant="ghost"
            @click="toggleExpanded(entry.id)"
          >
            {{ expandedEntryIds.has(entry.id) ? "Hide details" : "Show details" }}
          </BaseButton>
          <pre
            v-if="entry.context && expandedEntryIds.has(entry.id)"
            class="mt-2 p-2 bg-surface-dark rounded text-xs overflow-x-auto"
            >{{ JSON.stringify(entry.context, null, 2) }}</pre
          >
          <pre
            v-if="entry.traceback && expandedEntryIds.has(entry.id)"
            class="mt-2 p-2 bg-surface-dark rounded text-xs overflow-x-auto text-accent-red/80"
            >{{ entry.traceback }}</pre
          >
        </div>
      </Card>
    </div>
  </AdminPageLayout>
</template>
