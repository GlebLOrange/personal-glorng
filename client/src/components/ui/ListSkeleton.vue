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
    rowClass: "h-10",
    gapClass: "divide-y divide-surface-border/60",
  },
);
</script>

<template>
  <section :class="gapClass" aria-busy="true" :aria-label="label">
    <div
      v-for="i in rows"
      :key="i"
      :class="[rowClass, 'w-full animate-pulse rounded-md bg-surface-border/20 px-2']"
    />
  </section>
</template>
