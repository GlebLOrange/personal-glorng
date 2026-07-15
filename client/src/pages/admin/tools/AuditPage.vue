<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminFilterBar from "@/components/admin/AdminFilterBar.vue";
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
const action = ref("");
const requestId = ref("");
const actorId = ref("");
const resourceType = ref("");
const resourceId = ref("");
const page = ref(1);
const expandedEventIds = ref<Set<number>>(new Set());
const totalPages = computed(() => Math.ceil(total.value / ADMIN_LIST_PAGE_SIZE));
const hasPreviousPage = computed(() => page.value > 1);
const hasNextPage = computed(() => page.value < totalPages.value);

useScrollListFingerprint(
  () =>
    `${page.value}:${total.value}:${category.value}:${action.value}:${requestId.value}:${actorId.value}:${resourceType.value}:${resourceId.value}:${items.value[0]?.id ?? ""}`,
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
    if (action.value) params.action = action.value;
    if (requestId.value.trim()) params.request_id = requestId.value.trim();
    if (actorId.value.trim()) params.actor_id = Number(actorId.value.trim());
    if (resourceType.value.trim()) params.resource_type = resourceType.value.trim();
    if (resourceId.value.trim()) params.resource_id = Number(resourceId.value.trim());
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

function applyFilters(): void {
  page.value = 1;
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

function categoryClass(cat: string): string {
  return cat === "security"
    ? "bg-accent-red/20 text-accent-red border-accent-red/30"
    : "bg-accent-blue/20 text-accent-blue border-accent-blue/30";
}

onMounted(load);
</script>

<template>
  <AdminPageLayout title="audit log">
    <header class="page-intro">
      <p class="text-xs text-surface-muted">Persistent security and domain change trail</p>
    </header>

    <AdminFilterBar @apply="applyFilters">
      <BaseSelect v-model="category" label="Category" compact>
        <option value="">All</option>
        <option value="security">Security</option>
        <option value="domain">Domain</option>
      </BaseSelect>
      <BaseInput
        v-model="action"
        label="Action"
        compact
        placeholder="e.g. auth.login_success"
      />
      <BaseInput v-model="requestId" label="Request ID" compact placeholder="UUID" />
      <BaseInput v-model="actorId" label="Actor ID" compact placeholder="User ID" />
      <BaseInput
        v-model="resourceType"
        label="Resource type"
        compact
        placeholder="e.g. recipe"
      />
      <BaseInput v-model="resourceId" label="Resource ID" compact placeholder="Numeric ID" />
    </AdminFilterBar>

    <AdminListSkeleton v-if="loading" label="Loading audit events" />

    <ErrorState v-else-if="listError" :message="listError" show-retry @retry="load" />

    <EmptyState v-else-if="items.length === 0" description="No audit events found." />

    <div v-else class="min-w-0 space-y-1">
      <AdminListToolbar
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        item-label="events"
        ariaLabel="Audit pagination"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
      />
      <AdminListRow
        v-for="event in items"
        :key="event.id"
        interactive
        expandable
        :expanded="expandedEventIds.has(event.id)"
        @click="toggleExpanded(event.id)"
      >
        <template #badge>
          <StatusBadge :label="event.category" :class-name="categoryClass(event.category)" />
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
  </AdminPageLayout>
</template>
