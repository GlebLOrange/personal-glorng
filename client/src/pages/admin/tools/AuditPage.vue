<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from "vue";

import AdminDataRow from "@/components/admin/AdminDataRow.vue";
import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import PageShell from "@/components/layout/PageShell.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
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
import { auditCategoryClass } from "@/constants/filterColors";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useExpandableIds } from "@/composables/useExpandableIds";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { daysAgoIsoDate, isoDateLocal, yesterdayIsoDate } from "@/utils/dates";
import { formatDate } from "@/utils/format";

interface AuditEvent {
  id: number;
  occurred_at: string;
  category: string;
  action: string;
  actor_type: string;
  actor_id: number | null;
  source: string;
  resource_type: string | null;
  resource_id: number | null;
  metadata: Record<string, unknown> | null;
  request_id: string | null;
}

type PeriodFilter = "yesterday" | "today" | "7d" | "all";

const DEFAULT_CATEGORY = "security";
const DEFAULT_PERIOD: PeriodFilter = "yesterday";

type WhenSort = "when_desc" | "when_asc";

const items = ref<AuditEvent[]>([]);
const total = ref(0);
const { loading, lastError: listError, run: runLoad } = useApiAction({ silent: true });
const category = ref(DEFAULT_CATEGORY);
const page = ref(1);
const period = ref<PeriodFilter>(DEFAULT_PERIOD);
const sort = ref<WhenSort>("when_desc");

const whenAriaSort = computed(() => (sort.value === "when_asc" ? "ascending" : "descending"));
const whenIndicator = computed(() => (sort.value === "when_asc" ? " ↑" : " ↓"));
const { has: isExpanded, toggle: toggleExpanded, clear: clearExpanded } = useExpandableIds();
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");

const CATEGORY_FILTERS = [
  { label: "security", value: "security" },
  { label: "domain", value: "domain" },
] as const;

const PERIOD_FILTERS: { label: string; value: PeriodFilter }[] = [
  { label: "since yesterday", value: "yesterday" },
  { label: "today", value: "today" },
  { label: "last 7 days", value: "7d" },
  { label: "all", value: "all" },
];

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
const hasActiveFilters = computed(
  () => category.value !== DEFAULT_CATEGORY || period.value !== DEFAULT_PERIOD,
);
const activeFilterLabel = computed(() => {
  const categoryLabel = CATEGORY_FILTERS.find((chip) => chip.value === category.value)?.label;
  return [categoryLabel, periodLabel.value].filter(Boolean).join(" · ");
});
const emptyDescription = computed(() => `no ${category.value} audit events ${periodLabel.value}`);

useScrollListFingerprint(
  () =>
    `${page.value}:${total.value}:${category.value}:${period.value}:${items.value[0]?.id ?? ""}`,
);

async function load(): Promise<void> {
  const data = await runLoad(
    async () => {
      const params: Record<string, string | number> = {
        page: page.value,
        per_page: ADMIN_LIST_PAGE_SIZE,
        sort: sort.value,
      };
      if (category.value) params.category = category.value;
      if (dateFrom.value) params.date_from = dateFrom.value;
      const { data: response } = await api.get<{ items: AuditEvent[]; total: number }>(
        "/tools/audit",
        { params },
      );
      return response;
    },
    { errorMessage: "Failed to load audit events.", logContext: "audit.load" },
  );
  if (!data) return;
  items.value = data.items;
  total.value = data.total;
  clearExpanded();
}

function setCategoryFilter(next: string): void {
  category.value = next;
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

function clearFilters(): void {
  category.value = DEFAULT_CATEGORY;
  period.value = DEFAULT_PERIOD;
  page.value = 1;
  filterDropdownRef.value?.close();
  void load();
}

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

function actorLabel(event: AuditEvent): string {
  return event.actor_id ? `${event.actor_type}#${event.actor_id}` : event.actor_type;
}

function resourceLabel(event: AuditEvent): string | null {
  if (!event.resource_type) return null;
  return event.resource_id ? `${event.resource_type}#${event.resource_id}` : event.resource_type;
}

onMounted(load);
</script>

<template>
  <PageShell
    title="audit logs"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'audit logs' }]"
    back-to="/tools"
    max-width="5xl"
    body-width="column"
  >
    <AdminListSkeleton
      v-if="loading && items.length === 0 && !listError"
      label="Loading audit events"
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
                ...CATEGORY_FILTERS.map((chip) => chip.label),
                ...PERIOD_FILTERS.map((chip) => chip.label),
              ]"
              @clear="clearFilters"
            >
              <template #chips>
                <AdminFilterChip
                  v-for="chip in CATEGORY_FILTERS"
                  :key="chip.value"
                  :label="chip.label"
                  :active="category === chip.value"
                  :color-class="auditCategoryClass(chip.value)"
                  @click="setCategoryFilter(chip.value)"
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
            </AdminFilterDropdown>
          </template>
        </AdminListToolbar>
      </div>

      <ErrorState v-if="listError" class="mt-4" :message="listError" show-retry @retry="load" />

      <EmptyState v-else-if="items.length === 0" class="mt-4" :description="emptyDescription" />

      <div v-else class="mt-1 w-full min-w-0 self-stretch">
        <AdminDataTable table-label="audit log events">
          <template #header>
            <th :class="ADMIN_TH_CLASS">type</th>
            <th :class="ADMIN_TH_CLASS">who</th>
            <th :class="ADMIN_TH_CLASS" :aria-sort="whenAriaSort">
              <button
                type="button"
                :class="ADMIN_SORT_HEADER_BUTTON_CLASS"
                aria-label="sort by when"
                @click="toggleWhenSort"
              >
                <ChevronIcon class-name="size-3 shrink-0" />
                when{{ whenIndicator }}
              </button>
            </th>
            <th :class="ADMIN_TH_CLASS">title</th>
            <th :class="[ADMIN_TH_CLASS, 'w-px text-right']" scope="col">expand</th>
          </template>

          <AdminDataRow
            v-for="event in items"
            :key="event.id"
            interactive
            expandable
            :expanded="isExpanded(event.id)"
            :col-span="5"
            @click="toggleExpanded(event.id)"
          >
            <td :class="ADMIN_TD_CLASS">
              <StatusBadge
                :label="event.category"
                :class-name="auditCategoryClass(event.category)"
              />
            </td>
            <td :class="ADMIN_TD_MUTED_CLASS" :title="actorLabel(event)">
              {{ actorLabel(event) }}
            </td>
            <td :class="ADMIN_TD_MUTED_CLASS">{{ formatDate(event.occurred_at) }}</td>
            <td :class="ADMIN_TD_TITLE_CLASS">
              <p class="truncate text-sm text-surface-light" :title="event.action">
                {{ event.action }}
              </p>
              <p
                v-if="resourceLabel(event)"
                class="mt-0.5 truncate text-xs text-surface-mid"
                :title="resourceLabel(event)!"
              >
                {{ resourceLabel(event) }}
              </p>
            </td>
            <template #actions>
              <ChevronIcon
                direction="right"
                :open="isExpanded(event.id)"
                class-name="size-3.5 shrink-0 text-surface-muted"
              />
            </template>
            <template #detail>
              <p>
                actor: {{ event.actor_type }}
                <span v-if="event.actor_id">#{{ event.actor_id }}</span>
                · source: {{ event.source }}
              </p>
              <p v-if="event.resource_type">
                resource: {{ event.resource_type }}
                <span v-if="event.resource_id">#{{ event.resource_id }}</span>
              </p>
              <p v-if="event.request_id" class="font-data">request: {{ event.request_id }}</p>
              <pre
                v-if="event.metadata"
                class="mt-2 overflow-x-auto rounded bg-surface-dark p-2 text-xs"
                >{{ JSON.stringify(event.metadata, null, 2) }}</pre>
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
        item-label="events"
        aria-label="audit pagination"
        @first="goToPage(1)"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
        @last="goToPage(totalPages)"
      />
    </template>
  </PageShell>
</template>
