<script setup lang="ts">
import { ref } from "vue";

import BaseCard from "@/components/ui/BaseCard.vue";
import { statusBadgeClass, statusLabel } from "@/constants/taskStatus";
import { formatDate } from "@/utils/format";
import type { TaskIntakeItem } from "@/types";

defineProps<{
  intakes: TaskIntakeItem[];
  loading: boolean;
}>();

const showDebug = ref<Record<number, boolean>>({});

interface DraftFields {
  title?: string | null;
  scheduled_date?: string | null;
  scheduled_time?: string | null;
  description?: string | null;
  location?: string | null;
  reminder_minutes?: number | null;
  assignee_hint?: string | null;
}

function draftFields(draft: Record<string, unknown> | null): DraftFields {
  if (!draft) return {};
  return draft as DraftFields;
}

const draftEntries = [
  { key: "title", label: "Title" },
  { key: "scheduled_date", label: "Date" },
  { key: "scheduled_time", label: "Time" },
  { key: "location", label: "Location" },
  { key: "description", label: "Notes" },
  { key: "reminder_minutes", label: "Reminder (min)" },
  { key: "assignee_hint", label: "Assignee" },
] as const;

function toggleDebug(id: number): void {
  showDebug.value[id] = !showDebug.value[id];
}

const skeletonRows = 3;
</script>

<template>
  <div v-if="loading" class="flex flex-col gap-3">
    <BaseCard v-for="n in skeletonRows" :key="n" class="animate-pulse">
      <div class="h-4 w-32 bg-surface-border rounded mb-3" />
      <div class="h-3 w-full bg-surface-border rounded mb-2" />
      <div class="h-3 w-2/3 bg-surface-border rounded" />
    </BaseCard>
  </div>

  <div v-else-if="intakes.length === 0" class="text-surface-mid text-sm text-center py-8">
    No task intakes yet.
  </div>

  <div v-else class="space-y-3">
    <BaseCard v-for="item in intakes" :key="item.id">
      <div class="flex justify-between items-start gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-2 flex-wrap">
            <span class="text-surface-light font-bold text-sm">Intake #{{ item.id }}</span>
            <span
              :class="[
                'text-[10px] px-2 py-0.5 rounded-full border',
                statusBadgeClass(item.status),
              ]"
            >
              {{ statusLabel(item.status) }}
            </span>
            <span v-if="item.task_id" class="text-xs text-accent-blue">
              → Task #{{ item.task_id }}
            </span>
          </div>

          <p v-if="item.inbound_text" class="text-xs text-surface-mid mb-3">
            {{ item.inbound_text }}
          </p>

          <dl v-if="item.draft_json" class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 mb-3">
            <template v-for="entry in draftEntries" :key="entry.key">
              <template v-if="draftFields(item.draft_json)[entry.key] != null">
                <dt class="text-[10px] uppercase tracking-wide text-surface-mid">
                  {{ entry.label }}
                </dt>
                <dd class="text-xs text-surface-light mb-1 sm:mb-0">
                  {{ draftFields(item.draft_json)[entry.key] }}
                </dd>
              </template>
            </template>
          </dl>

          <button
            v-if="item.draft_json"
            type="button"
            class="text-[10px] text-accent-blue hover:underline"
            @click="toggleDebug(item.id)"
          >
            {{ showDebug[item.id] ? "Hide debug JSON" : "Show debug JSON" }}
          </button>
          <pre
            v-if="item.draft_json && showDebug[item.id]"
            class="text-[10px] text-surface-mid bg-surface-dark/50 rounded p-2 overflow-x-auto mt-2"
            >{{ JSON.stringify(item.draft_json, null, 2) }}</pre
          >
        </div>
        <span class="text-[10px] text-surface-mid shrink-0">
          {{ formatDate(item.created_at) }}
        </span>
      </div>
    </BaseCard>
  </div>
</template>
