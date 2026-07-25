<script setup lang="ts">
withDefaults(
  defineProps<{
    rows?: number;
    label?: string;
    /** Row height class — dense admin rows vs taller content cards */
    rowClass?: string;
    /** Spacing between skeleton rows — prefer divide for list parity */
    gapClass?: string;
  }>(),
  {
    rows: 5,
    label: "Loading list",
    rowClass: "h-9",
    gapClass: "divide-y divide-surface-border/40",
  },
);
</script>

<template>
  <section :class="gapClass" aria-busy="true" :aria-label="label">
    <div
      v-for="i in rows"
      :key="i"
      :class="[rowClass, 'w-full animate-pulse rounded-lg bg-surface-border/20 px-2 py-1.5']"
    />
  </section>
</template>
