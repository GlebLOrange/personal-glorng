<script setup lang="ts">
import { Card } from "@/components/ui/card";

withDefaults(
  defineProps<{
    rows?: number;
    label?: string;
  }>(),
  {
    rows: 8,
    label: "Loading list",
  },
);
</script>

<template>
  <section class="space-y-1" aria-busy="true" :aria-label="label">
    <Card v-for="i in rows" :key="i" variant="dense" class="h-9 animate-pulse" />
  </section>
</template>
