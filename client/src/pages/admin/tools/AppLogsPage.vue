<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, useTemplateRef } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { logLevelClass } from "@/constants/filterColors";
import { httpStatusClass } from "@/constants/httpStatusColors";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useExpandableIds } from "@/composables/useExpandableIds";
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
const { loading, lastError: listError, run: runLoad } = useApiAction({ silent: true });
const level = ref("");
const requestId = ref("");
const page = ref(1);
const { has: isExpanded, toggle: toggleExpanded, clear: clearExpanded } = useExpandableIds();
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");

const LEVEL_FILTERS = [
  { label: "debug", value: "debug" },
  { label: "info", value: "info" },
  { label: "warning", value: "warning" },
  { label: "error", value: "error" },
] as const;

/** Don't hit the API for partial request-id typing. */
const MIN_REQUEST_ID_LENGTH = 3;

const totalPages = computed(() => Math.ceil(total.value / ADMIN_LIST_PAGE_SIZE));
const hasPreviousPage = computed(() => page.value > 1);
const hasNextPage = computed(() => page.value < totalPages.value);
const appliedRequestId = computed(() => {
  const value = requestId.value.trim();
  return value.length >= MIN_REQUEST_ID_LENGTH ? value : "";
});
const hasActiveFilters = computed(() => Boolean(level.value || appliedRequestId.value));
const activeFilterLabel = computed(() => {
  const parts: string[] = [];
  if (level.value) parts.push(level.value);
  if (appliedRequestId.value) parts.push(appliedRequestId.value);
  return parts.length ? parts.join(", ") : undefined;
});

useScrollListFingerprint(
  () =>
    `${page.value}:${total.value}:${level.value}:${appliedRequestId.value}:${items.value[0]?.id ?? ""}`,
);

async function load(): Promise<void> {
  const data = await runLoad(
    async () => {
      const params: Record<string, string | number> = {
        page: page.value,
        per_page: ADMIN_LIST_PAGE_SIZE,
      };
      if (level.value) params.level = level.value;
      if (appliedRequestId.value) params.request_id = appliedRequestId.value;
      const { data: response } = await api.get<{ items: AppLogEntry[]; total: number }>(
        "/tools/app-logs",
        { params },
      );
      return response;
    },
    { errorMessage: "Failed to load app logs.", logContext: "appLogs.load" },
  );
  if (!data) return;
  items.value = data.items;
  total.value = data.total;
  clearExpanded();
}

function setLevelFilter(next: string): void {
  level.value = next;
  page.value = 1;
  filterDropdownRef.value?.close();
  void load();
}

let requestIdTimer: ReturnType<typeof setTimeout> | undefined;
let lastAppliedRequestId = "";

function onRequestIdChange(value: string | number | null | undefined): void {
  requestId.value = String(value ?? "");
  clearTimeout(requestIdTimer);
  requestIdTimer = setTimeout(() => {
    const next = appliedRequestId.value;
    // Reload when a 3+ char filter applies, or when clearing a previously applied one.
    if (next === lastAppliedRequestId) return;
    lastAppliedRequestId = next;
    page.value = 1;
    void load();
  }, 300);
}

function clearFilters(): void {
  clearTimeout(requestIdTimer);
  level.value = "";
  requestId.value = "";
  lastAppliedRequestId = "";
  page.value = 1;
  void load();
}

onUnmounted(() => {
  clearTimeout(requestIdTimer);
});

function goToPage(nextPage: number): void {
  if (nextPage < 1 || (totalPages.value > 0 && nextPage > totalPages.value)) return;
  page.value = nextPage;
  void load();
}

function onRowClick(entry: AppLogEntry): void {
  if (hasDetails(entry)) toggleExpanded(entry.id);
}

function hasDetails(entry: AppLogEntry): boolean {
  return Boolean(entry.context || entry.traceback || entry.error || entry.request_id);
}

function contextStatus(entry: AppLogEntry): number | null {
  const status = entry.context?.status;
  return typeof status === "number" && Number.isFinite(status) ? status : null;
}

onMounted(load);
</script>

<template>
  <AdminPageLayout title="app logs">
    <AdminListSkeleton
      v-if="loading && items.length === 0 && !listError"
      label="Loading app logs"
    />

    <template v-else>
      <AdminListToolbar>
        <template #start>
          <AdminFilterDropdown
            ref="filterDropdown"
            :has-active-filters="hasActiveFilters"
            :active-label="activeFilterLabel"
            :option-labels="LEVEL_FILTERS.map((chip) => chip.label)"
            @clear="clearFilters"
          >
            <template #chips>
              <AdminFilterChip
                v-for="chip in LEVEL_FILTERS"
                :key="chip.value"
                :label="chip.label"
                :active="level === chip.value"
                :color-class="logLevelClass(chip.value)"
                @click="setLevelFilter(chip.value)"
              />
            </template>
            <BaseInput
              :model-value="requestId"
              compact
              placeholder="request id (3+ chars)"
              aria-label="request id"
              @update:model-value="onRequestIdChange"
            />
          </AdminFilterDropdown>
        </template>
      </AdminListToolbar>

      <ErrorState v-if="listError" class="mt-4" :message="listError" show-retry @retry="load" />

      <EmptyState v-else-if="items.length === 0" class="mt-4" description="no log entries found" />

      <div v-else class="mt-1 min-w-0 space-y-2">
        <AdminListRow
          v-for="entry in items"
          :key="entry.id"
          :interactive="hasDetails(entry)"
          :expandable="hasDetails(entry)"
          :expanded="isExpanded(entry.id)"
          :hoverable="hasDetails(entry)"
          :status-class="logLevelClass(entry.level)"
          @click="onRowClick(entry)"
        >
          <template #badge>
            <div class="flex items-center gap-1">
              <StatusBadge :label="entry.level" :class-name="logLevelClass(entry.level)" />
              <StatusBadge
                v-if="contextStatus(entry) !== null"
                :label="String(contextStatus(entry))"
                :class-name="httpStatusClass(contextStatus(entry)!)"
              />
            </div>
          </template>
          <template #primary>
            <span class="lowercase" :title="entry.message.toLowerCase()">{{ entry.message }}</span>
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
              >{{ JSON.stringify(entry.context, null, 2) }}</pre>
            <pre
              v-if="entry.traceback"
              class="mt-2 overflow-x-auto rounded bg-surface-dark p-2 text-xs text-status-error/80"
              >{{ entry.traceback }}</pre>
          </template>
        </AdminListRow>
      </div>

      <AdminListFooter
        v-if="!listError"
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        :loading="loading"
        item-label="entries"
        aria-label="app logs pagination"
        @first="goToPage(1)"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
        @last="goToPage(totalPages)"
      />
    </template>
  </AdminPageLayout>
</template>
