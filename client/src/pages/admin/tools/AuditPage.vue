<script setup lang="ts">
import { onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
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
const category = ref("");
const action = ref("");
const page = ref(1);
const { toast } = useNotify();

async function load(): Promise<void> {
  loading.value = true;
  try {
    const params: Record<string, string | number> = { page: page.value, per_page: 50 };
    if (category.value) params.category = category.value;
    if (action.value) params.action = action.value;
    const { data } = await api.get<{ items: AuditEvent[]; total: number }>("/tools/audit", {
      params,
    });
    items.value = data.items;
    total.value = data.total;
  } catch (err) {
    console.error(err);
    toast("Failed to load audit events", "error");
  } finally {
    loading.value = false;
  }
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
    <p class="text-surface-muted text-xs mb-6 -mt-4">Persistent security and domain change trail</p>

    <BaseCard class="mb-6">
      <div class="flex flex-wrap gap-3 items-end">
        <label class="text-xs text-surface-mid">
          Category
          <select
            v-model="category"
            class="block mt-1 bg-surface-dark border border-surface-border rounded px-2 py-1 text-sm"
          >
            <option value="">All</option>
            <option value="security">Security</option>
            <option value="domain">Domain</option>
          </select>
        </label>
        <label class="text-xs text-surface-mid">
          Action
          <input
            v-model="action"
            type="text"
            placeholder="e.g. auth.login_success"
            class="block mt-1 bg-surface-dark border border-surface-border rounded px-2 py-1 text-sm"
          />
        </label>
        <BaseButton size="sm" @click="load">Filter</BaseButton>
      </div>
    </BaseCard>

    <p v-if="loading" class="text-surface-mid text-sm animate-pulse">Loading...</p>

    <div v-else-if="items.length === 0" class="text-surface-mid text-sm">
      No audit events found.
    </div>

    <div v-else class="space-y-3">
      <p class="text-xs text-surface-muted">{{ total }} events total</p>
      <BaseCard v-for="event in items" :key="event.id" class="text-sm">
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <span class="text-xs px-2 py-0.5 rounded" :class="categoryClass(event.category)">
            {{ event.category }}
          </span>
          <span class="font-mono text-surface-light">{{ event.action }}</span>
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
          <p v-if="event.request_id" class="font-mono">Request: {{ event.request_id }}</p>
          <pre
            v-if="event.metadata"
            class="mt-2 p-2 bg-surface-dark rounded text-xs overflow-x-auto"
            >{{ JSON.stringify(event.metadata, null, 2) }}</pre
          >
        </div>
      </BaseCard>
    </div>
  </AdminPageLayout>
</template>
