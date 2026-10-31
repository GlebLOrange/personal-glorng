<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, useTemplateRef } from "vue";

import AdminDataRow from "@/components/admin/AdminDataRow.vue";
import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import {
  ADMIN_SORT_HEADER_BUTTON_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TD_TITLE_CLASS,
  ADMIN_TH_CLASS,
} from "@/constants/adminDataTable";
import { logLevelClass } from "@/constants/filterColors";
import { httpStatusClass } from "@/constants/httpStatusColors";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useExpandableIds } from "@/composables/useExpandableIds";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { daysAgoIsoDate, isoDateLocal, yesterdayIsoDate } from "@/utils/dates";
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

type PeriodFilter = "yesterday" | "today" | "7d" | "all";

const DEFAULT_LEVEL = "error";
const DEFAULT_PERIOD: PeriodFilter = "yesterday";

type WhenSort = "when_desc" | "when_asc";

const items = ref<AppLogEntry[]>([]);
const total = ref(0);
const { loading, lastError: listError, run: runLoad } = useApiAction({ silent: true });
const level = ref(DEFAULT_LEVEL);
const requestId = ref("");
const page = ref(1);
const period = ref<PeriodFilter>(DEFAULT_PERIOD);
const sort = ref<WhenSort>("when_desc");

const whenAriaSort = computed(() => (sort.value === "when_asc" ? "ascending" : "descending"));
const whenIndicator = computed(() => (sort.value === "when_asc" ? " ↑" : " ↓"));
const { has: isExpanded, toggle: toggleExpanded, clear: clearExpanded } = useExpandableIds();
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");

const LEVEL_FILTERS = [
  { label: "debug", value: "debug" },
  { label: "info", value: "info" },
  { label: "warning", value: "warning" },
  { label: "error", value: "error" },
] as const;

const PERIOD_FILTERS: { label: string; value: PeriodFilter }[] = [
  { label: "since yesterday", value: "yesterday" },
  { label: "today", value: "today" },
  { label: "last 7 days", value: "7d" },
  { label: "all", value: "all" },
];

/** Don't hit the API for partial request-id typing. */
const MIN_REQUEST_ID_LENGTH = 3;

const PERIOD_CHIP_CLASS = "bg-surface-mid/15 text-surface-mid border-surface-border";

function dateFromForPeriod(value: PeriodFilter): string | undefined {
  if (value === "all") return undefined;
  if (value === "today") return isoDateLocal();
  if (value === "7d") return daysAgoIsoDate(7);
  return yesterdayIsoDate();
}

const periodLabel = computed(
  () => PERIOD_FILTERS.find((chip) => chip.value === period.value)?.label ?? "since yesterday",
);
const dateFrom = computed(() => dateFromForPeriod(period.value));

const totalPages = computed(() => Math.ceil(total.value / ADMIN_LIST_PAGE_SIZE));
const hasPreviousPage = computed(() => page.value > 1);
const hasNextPage = computed(() => page.value < totalPages.value);
const appliedRequestId = computed(() => {
  const value = requestId.value.trim();
  return value.length >= MIN_REQUEST_ID_LENGTH ? value : "";
});
const hasActiveFilters = computed(
  () =>
    level.value !== DEFAULT_LEVEL ||
    period.value !== DEFAULT_PERIOD ||
    Boolean(appliedRequestId.value),
);
const activeFilterLabel = computed(() => {
  const parts: string[] = [];
  if (level.value) parts.push(level.value);
  parts.push(periodLabel.value);
  if (appliedRequestId.value) parts.push(appliedRequestId.value);
  return parts.join(" · ");
});
const emptyDescription = computed(() => `no ${level.value} logs ${periodLabel.value}`);

useScrollListFingerprint(
  () =>
    `${page.value}:${total.value}:${level.value}:${appliedRequestId.value}:${period.value}:${items.value[0]?.id ?? ""}`,
);

async function load(): Promise<void> {
  const data = await runLoad(
    async () => {
      const params: Record<string, string | number> = {
        page: page.value,
        per_page: ADMIN_LIST_PAGE_SIZE,
        sort: sort.value,
      };
      if (level.value) params.level = level.value;
      if (appliedRequestId.value) params.request_id = appliedRequestId.value;
      if (dateFrom.value) params.date_from = dateFrom.value;
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

function setPeriodFilter(next: PeriodFilter): void {
  period.value = next;
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
  level.value = DEFAULT_LEVEL;
  requestId.value = "";
  period.value = DEFAULT_PERIOD;
  lastAppliedRequestId = "";
  page.value = 1;
  void load();
}

function loggerLabel(entry: AppLogEntry): string {
  return entry.error_type ? `${entry.logger} · ${entry.error_type}` : entry.logger;
}

onUnmounted(() => {
  clearTimeout(requestIdTimer);
});

function goToPage(nextPage: number): void {
  if (nextPage < 1 || (totalPages.value > 0 && nextPage > totalPages.value)) return;
  page.value = nextPage;
  void load();
}

function toggleWhenSort(): void {
  sort.value = sort.value === "when_desc" ? "when_asc" : "when_desc";
  page.value = 1;
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
  <PageShell
    title="app logs"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'app logs' }]"
    back-to="/tools"
    max-width="5xl"
    :narrow="false"
    tool
  >
    <AdminListSkeleton
      v-if="loading && items.length === 0 && !listError"
      label="Loading app logs"
    />

    <template v-else>
      <div class="page-tool-actions">
        <AdminListToolbar>
          <template #start>
            <AdminFilterDropdown
              ref="filterDropdown"
              :has-active-filters="hasActiveFilters"
              :active-label="activeFilterLabel"
              :option-labels="[
                ...LEVEL_FILTERS.map((chip) => chip.label),
                ...PERIOD_FILTERS.map((chip) => chip.label),
              ]"
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
                <AdminFilterChip
                  v-for="chip in PERIOD_FILTERS"
                  :key="chip.value"
                  :label="chip.label"
                  :active="period === chip.value"
                  :color-class="PERIOD_CHIP_CLASS"
                  @click="setPeriodFilter(chip.value)"
                />
              </template>
              <BaseInput
                :model-value="requestId"
                compact
                auto-width
                placeholder="request id (3+ chars)"
                aria-label="request id"
                @update:model-value="onRequestIdChange"
              />
            </AdminFilterDropdown>
          </template>
        </AdminListToolbar>
      </div>

      <ErrorState v-if="listError" class="mt-4" :message="listError" show-retry @retry="load" />

      <EmptyState v-else-if="items.length === 0" class="mt-4" :description="emptyDescription" />

      <div v-else class="mt-1 min-w-0">
        <AdminDataTable table-label="app log entries">
          <template #header>
            <th :class="ADMIN_TH_CLASS">type</th>
            <th :class="ADMIN_TH_CLASS" :aria-sort="whenAriaSort">
              <button
                type="button"
                :class="ADMIN_SORT_HEADER_BUTTON_CLASS"
                aria-label="sort by when"
                @click="toggleWhenSort"
              >
                when{{ whenIndicator }}
              </button>
            </th>
            <th :class="ADMIN_TH_CLASS">logger</th>
            <th :class="ADMIN_TH_CLASS">info</th>
          </template>

          <AdminDataRow
            v-for="entry in items"
            :key="entry.id"
            :interactive="hasDetails(entry)"
            :expandable="hasDetails(entry)"
            :expanded="isExpanded(entry.id)"
            :col-span="4"
            @click="onRowClick(entry)"
          >
            <td :class="ADMIN_TD_CLASS">
              <div class="flex items-center gap-1">
                <StatusBadge :label="entry.level" :class-name="logLevelClass(entry.level)" />
                <StatusBadge
                  v-if="contextStatus(entry) !== null"
                  :label="String(contextStatus(entry))"
                  :class-name="httpStatusClass(contextStatus(entry)!)"
                />
              </div>
            </td>
            <td :class="ADMIN_TD_MUTED_CLASS">{{ formatDate(entry.occurred_at) }}</td>
            <td :class="[ADMIN_TD_MUTED_CLASS, 'font-data']" :title="loggerLabel(entry)">
              {{ loggerLabel(entry) }}
            </td>
            <td :class="ADMIN_TD_TITLE_CLASS">
              <p
                class="truncate text-sm lowercase text-surface-light"
                :title="entry.message.toLowerCase()"
              >
                {{ entry.message }}
              </p>
            </td>
            <template v-if="hasDetails(entry)" #detail>
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
          </AdminDataRow>
        </AdminDataTable>
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
  </PageShell>
</template>
