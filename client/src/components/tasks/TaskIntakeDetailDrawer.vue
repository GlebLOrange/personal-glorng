<script setup lang="ts">
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { statusBadgeClass, statusLabel } from "@/constants/taskStatus";
import { formatDate } from "@/utils/format";
import type { TaskIntakeItem } from "@/types";

defineProps<{
  open: boolean;
  intake: TaskIntakeItem | null;
}>();

const emit = defineEmits<{ close: [] }>();

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
</script>

<template>
  <BaseDrawer
    :open="open && intake !== null"
    :title="intake ? `Intake #${intake.id}` : 'Intake'"
    max-width="md"
    @close="emit('close')"
  >
    <template v-if="intake">
      <div class="mb-4 flex flex-wrap items-center gap-2">
        <StatusBadge
          :label="statusLabel(intake.status)"
          :class-name="statusBadgeClass(intake.status)"
        />
        <span v-if="intake.task_id" class="text-xs text-accent-blue">→ Task #{{ intake.task_id }}</span>
        <span class="text-xs text-surface-muted">{{ formatDate(intake.created_at) }}</span>
      </div>

      <p v-if="intake.inbound_text" class="mb-4 text-sm text-surface-mid">{{ intake.inbound_text }}</p>

      <dl v-if="intake.draft_json" class="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
        <template v-for="entry in draftEntries" :key="entry.key">
          <template v-if="draftFields(intake.draft_json)[entry.key] != null">
            <dt class="text-[10px] uppercase tracking-wide text-surface-mid">{{ entry.label }}</dt>
            <dd class="text-xs text-surface-light">{{ draftFields(intake.draft_json)[entry.key] }}</dd>
          </template>
        </template>
      </dl>

      <details
        v-if="intake.draft_json"
        class="mt-4 text-sm text-surface-mid"
      >
        <summary class="cursor-pointer select-none hover:text-surface-light">raw draft</summary>
        <pre
          class="mt-2 overflow-x-auto rounded bg-surface-dark/50 p-2 text-[10px] text-surface-mid"
        >{{ JSON.stringify(intake.draft_json, null, 2) }}</pre>
      </details>
    </template>
  </BaseDrawer>
</template>
