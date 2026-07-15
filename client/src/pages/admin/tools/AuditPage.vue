<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import { Card } from "@/components/ui/card";
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

const PER_PAGE = 50;
const items = ref<AuditEvent[]>([]);
const total = ref(0);
const loading = ref(false);
const listError = ref<string | null>(null);
const category = ref("");
const action = ref("");
const page = ref(1);
const expandedEventIds = ref<Set<number>>(new Set());
const totalPages = computed(() => Math.ceil(total.value / PER_PAGE));
const hasPreviousPage = computed(() => page.value > 1);
const hasNextPage = computed(() => page.value < totalPages.value);

useScrollListFingerprint(
  () =>
    `${page.value}:${total.value}:${category.value}:${action.value}:${items.value[0]?.id ?? ""}`,
);

async function load(): Promise<void> {
  loading.value = true;
  listError.value = null;
  try {
    const params: Record<string, string | number> = { page: page.value, per_page: PER_PAGE };
    if (category.value) params.category = category.value;
    if (action.value) params.action = action.value;
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

function categoryClass(cat: string): string {
  return cat === "security"
    ? "bg-accent-red/20 text-accent-red"
    : "bg-accent-blue/20 text-accent-blue";
}

onMounted(load);
</script>

<template>
  <AdminPageLayout title="audit log">
    <header class="page-intro">
      <p class="text-xs text-surface-muted">Persistent security and domain change trail</p>
    </header>

    <Card class="mb-6">
      <div class="flex flex-wrap gap-3 items-end">
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
        <BaseButton size="sm" @click="applyFilters">Filter</BaseButton>
      </div>
    </Card>

    <section v-if="loading" class="space-y-3" aria-busy="true" aria-label="Loading audit events">
      <Card v-for="i in 5" :key="i" class="h-24 animate-pulse" />
    </section>

    <ErrorState
      v-else-if="listError"
      :message="listError"
      show-retry
      @retry="load"
    />

    <EmptyState v-else-if="items.length === 0" description="No audit events found." />

    <div v-else class="min-w-0 space-y-3">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <p class="text-xs text-surface-muted">
          {{ total }} events total · page {{ page }} of {{ Math.max(totalPages, 1) }}
        </p>
        <div class="flex items-center gap-2">
          <BaseButton
            size="sm"
            variant="ghost"
            :disabled="!hasPreviousPage"
            @click="goToPage(page - 1)"
          >
            Previous
          </BaseButton>
          <BaseButton
            size="sm"
            variant="ghost"
            :disabled="!hasNextPage"
            @click="goToPage(page + 1)"
          >
            Next
          </BaseButton>
        </div>
      </div>
      <Card v-for="event in items" :key="event.id" class="text-sm">
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <span class="text-xs px-2 py-0.5 rounded" :class="categoryClass(event.category)">
            {{ event.category }}
          </span>
          <span class="min-w-0 break-words text-surface-light">{{ event.action }}</span>
          <span class="text-xs text-surface-muted ml-auto">
            {{ formatDate(event.occurred_at) }}
          </span>
        </div>
        <div class="text-xs text-surface-mid space-y-1">
          <p>
            Actor: {{ event.actor_type }}
            <span v-if="event.actor_id">#{{ event.actor_id }}</span>
            · Source: {{ event.source }}
          </p>
          <p v-if="event.resource_type">
            Resource: {{ event.resource_type }}
            <span v-if="event.resource_id">#{{ event.resource_id }}</span>
          </p>
          <p v-if="event.request_id" class="font-data text-xs">Request: {{ event.request_id }}</p>
          <BaseButton
            v-if="event.metadata"
            size="sm"
            variant="ghost"
            @click="toggleExpanded(event.id)"
          >
            {{ expandedEventIds.has(event.id) ? "Hide metadata" : "Show metadata" }}
          </BaseButton>
          <pre
            v-if="event.metadata && expandedEventIds.has(event.id)"
            class="mt-2 p-2 bg-surface-dark rounded text-xs overflow-x-auto"
            >{{ JSON.stringify(event.metadata, null, 2) }}</pre
          >
        </div>
      </Card>
    </div>
  </AdminPageLayout>
</template>
