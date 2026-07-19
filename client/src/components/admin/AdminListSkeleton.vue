<script setup lang="ts">
import ListSkeleton from "@/components/ui/ListSkeleton.vue";

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
  <ListSkeleton :rows="rows" :label="label" row-class="h-9" />
</template>
