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
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
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

const items = ref<AuditEvent[]>([]);
const total = ref(0);
const loading = ref(false);
const listError = ref<string | null>(null);
const category = ref("");
const page = ref(1);
const expandedEventIds = ref<Set<number>>(new Set());
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");

const CATEGORY_FILTERS = [
  { label: "security", value: "security" },
  { label: "domain", value: "domain" },
] as const;

const totalPages = computed(() => Math.ceil(total.value / ADMIN_LIST_PAGE_SIZE));
const hasPreviousPage = computed(() => page.value > 1);
const hasNextPage = computed(() => page.value < totalPages.value);
const hasActiveFilters = computed(() => Boolean(category.value));
const activeFilterLabel = computed(
  () => CATEGORY_FILTERS.find((chip) => chip.value === category.value)?.label,
);

useScrollListFingerprint(
  () => `${page.value}:${total.value}:${category.value}:${items.value[0]?.id ?? ""}`,
);

async function load(): Promise<void> {
  loading.value = true;
  listError.value = null;
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      per_page: ADMIN_LIST_PAGE_SIZE,
    };
    if (category.value) params.category = category.value;
    const { data } = await api.get<{ items: AuditEvent[]; total: number }>("/tools/audit", {
      params,
    });
    items.value = data.items;
    total.value = data.total;
    expandedEventIds.value = new Set();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    listError.value = "Failed to load audit events.";
  } finally {
    loading.value = false;
  }
}

function setCategoryFilter(next: string): void {
  category.value = next;
  page.value = 1;
  filterDropdownRef.value?.close();
  void load();
}

function clearFilters(): void {
  category.value = "";
  page.value = 1;
  filterDropdownRef.value?.close();
  void load();
}

function goToPage(nextPage: number): void {
  if (nextPage < 1 || (totalPages.value > 0 && nextPage > totalPages.value)) return;
  page.value = nextPage;
  void load();
}

function toggleExpanded(eventId: number): void {
  const next = new Set(expandedEventIds.value);
  if (next.has(eventId)) {
    next.delete(eventId);
  } else {
    next.add(eventId);
  }
  expandedEventIds.value = next;
}

function actorLabel(event: AuditEvent): string {
  const actor = event.actor_id ? `${event.actor_type}#${event.actor_id}` : event.actor_type;
  return actor;
}

onMounted(load);
</script>

<template>
  <AdminPageLayout title="audit log">
    <AdminListSkeleton v-if="loading && items.length === 0 && !listError" label="Loading audit events" />

    <template v-else>
      <AdminListToolbar>
        <template #start>
          <AdminFilterDropdown
            ref="filterDropdown"
            :has-active-filters="hasActiveFilters"
            :active-label="activeFilterLabel"
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
            </template>
          </AdminFilterDropdown>
        </template>
      </AdminListToolbar>

      <ErrorState v-if="listError" class="mt-4" :message="listError" show-retry @retry="load" />

      <EmptyState v-else-if="items.length === 0" class="mt-4" description="No audit events found." />

      <div v-else class="min-w-0 mt-1 space-y-1">
        <AdminListRow
          v-for="event in items"
          :key="event.id"
          interactive
          expandable
          :expanded="expandedEventIds.has(event.id)"
          @click="toggleExpanded(event.id)"
        >
          <template #badge>
            <StatusBadge :label="event.category" :class-name="auditCategoryClass(event.category)" />
          </template>
          <template #primary>
            <span :title="event.action">{{ event.action }}</span>
          </template>
          <template #meta>
            <span>{{ actorLabel(event) }}</span>
          </template>
          <template #time>{{ formatDate(event.occurred_at) }}</template>
          <template #detail>
            <p>
              Actor: {{ event.actor_type }}
              <span v-if="event.actor_id">#{{ event.actor_id }}</span>
              · Source: {{ event.source }}
            </p>
            <p v-if="event.resource_type">
              Resource: {{ event.resource_type }}
              <span v-if="event.resource_id">#{{ event.resource_id }}</span>
            </p>
            <p v-if="event.request_id" class="font-data">Request: {{ event.request_id }}</p>
            <pre
              v-if="event.metadata"
              class="mt-2 overflow-x-auto rounded bg-surface-dark p-2 text-xs"
              >{{ JSON.stringify(event.metadata, null, 2) }}</pre
            >
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
        ariaLabel="Audit pagination"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
      />
    </template>
  </AdminPageLayout>
</template>
