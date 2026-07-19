<script setup lang="ts">
import { Card } from "@/components/ui/card";

withDefaults(
  defineProps<{
    rows?: number;
    label?: string;
    /** Row height class — dense admin rows vs taller content cards */
    rowClass?: string;
    /** Spacing between skeleton rows */
    gapClass?: string;
  }>(),
  {
    rows: 5,
    label: "Loading list",
    rowClass: "h-9",
    gapClass: "space-y-1",
  },
);
</script>

<template>
  <section :class="gapClass" aria-busy="true" :aria-label="label">
    <Card v-for="i in rows" :key="i" variant="dense" :class="[rowClass, 'animate-pulse']" />
  </section>
</template>
