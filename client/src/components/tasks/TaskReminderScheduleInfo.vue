<script setup lang="ts">
import { useId } from "vue";

import FieldHelp from "@/components/ui/FieldHelp.vue";
import {
  FIELD_LABEL_TEXT_CLASS,
  FIELD_NOTCH_BG_CLASS,
  FIELD_NOTCH_ROW_CLASS,
  FIELD_WRAPPER_CLASS,
} from "@/constants/formClasses";

/**
 * Chip minute offsets mirror server DEFAULT_EARLY_REMINDER_MINUTES (90, 60, 30)
 * plus at-start — do not invent alternate schedules here.
 */
const EARLY_REMINDER_MINUTES = [90, 60, 30] as const;

const CHIP_LABELS: readonly string[] = [
  ...EARLY_REMINDER_MINUTES.map((minutes) => `${minutes} min`),
  "at start",
];

/** Same wording AT heard from the former plain STATIC_REMINDER_LABEL paragraph. */
const SCHEDULE_ARIA_LABEL = "Reminders: 90 / 60 / 30 min before + at start";

const HELP_TIP = "telegram and calendar · fixed schedule";

const fieldId = useId();
const hintId = `${fieldId}-hint`;
</script>

<template>
  <div :class="[FIELD_WRAPPER_CLASS, 'pt-2.5']">
    <div
      :id="fieldId"
      role="group"
      :aria-label="SCHEDULE_ARIA_LABEL"
      :aria-describedby="hintId"
      class="relative box-border flex min-h-10 w-full min-w-0 items-center overflow-visible rounded-lg bg-surface-dark ring-1 ring-inset ring-surface-border"
    >
      <div class="flex min-w-0 flex-1 flex-wrap items-center gap-1.5 px-3 py-1.5" aria-hidden="true">
        <span
          v-for="label in CHIP_LABELS"
          :key="label"
          class="inline-flex cursor-default items-center rounded-md border border-surface-border bg-surface-card px-2 py-0.5 text-xs text-surface-mid"
        >
          {{ label }}
        </span>
      </div>
    </div>

    <div :class="[FIELD_NOTCH_ROW_CLASS, FIELD_NOTCH_BG_CLASS]">
      <span :class="FIELD_LABEL_TEXT_CLASS">reminders</span>
      <span class="pointer-events-auto">
        <FieldHelp size="sm" align="start" :text="HELP_TIP" :content-id="hintId" />
      </span>
    </div>
  </div>
</template>
