<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
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

const items = ref<AuditEvent[]>([]);
const total = ref(0);
const { loading, lastError: listError, run: runLoad } = useApiAction({ silent: true });
const category = ref(DEFAULT_CATEGORY);
const page = ref(1);
const period = ref<PeriodFilter>(DEFAULT_PERIOD);
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
const emptyDescription = computed(
  () => `no ${category.value} audit events ${periodLabel.value}`,
);

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

function actorLabel(event: AuditEvent): string {
  return event.actor_id ? `${event.actor_type}#${event.actor_id}` : event.actor_type;
}

function eventMeta(event: AuditEvent): string {
  const actor = actorLabel(event);
  if (!event.resource_type) return actor;
  const resource = event.resource_id
    ? `${event.resource_type}#${event.resource_id}`
    : event.resource_type;
  return `${actor} · ${resource}`;
}

onMounted(load);
</script>

<template>
  <AdminPageLayout title="audit logs">
    <AdminListSkeleton
      v-if="loading && items.length === 0 && !listError"
      label="Loading audit events"
    />

    <template v-else>
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

      <ErrorState v-if="listError" class="mt-4" :message="listError" show-retry @retry="load" />

      <EmptyState
        v-else-if="items.length === 0"
        class="mt-4"
        :description="emptyDescription"
      />

      <div v-else class="mt-1 min-w-0">
        <AdminListRow
          v-for="event in items"
          :key="event.id"
          interactive
          expandable
          :expanded="isExpanded(event.id)"
          :status-class="auditCategoryClass(event.category)"
          @click="toggleExpanded(event.id)"
        >
          <template #badge>
            <StatusBadge :label="event.category" :class-name="auditCategoryClass(event.category)" />
          </template>
          <template #primary>
            <span :title="event.action">{{ event.action }}</span>
          </template>
          <template #meta>
            <span :title="eventMeta(event)">{{ eventMeta(event) }}</span>
          </template>
          <template #time>{{ formatDate(event.occurred_at) }}</template>
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
        item-label="events"
        aria-label="audit pagination"
        @first="goToPage(1)"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
        @last="goToPage(totalPages)"
      />
    </template>
  </AdminPageLayout>
</template>
