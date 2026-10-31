<script setup lang="ts">
/**
 * Fixed create schedule — same meaning as server STATIC_REMINDER_LABEL.
 * Do not invent alternate schedules or a create-time picker here.
 */
const STATIC_REMINDER_LABEL = "Reminders: 90 / 60 / 30 min before + at start";
</script>

<template>
  <p class="text-sm leading-relaxed text-surface-mid">
    {{ STATIC_REMINDER_LABEL }}
  </p>
</template>
