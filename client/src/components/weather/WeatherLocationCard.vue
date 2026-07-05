<script setup lang="ts">
import { computed } from "vue";

import WeatherSummaryCard from "@/components/weather/WeatherSummaryCard.vue";

const props = defineProps<{
  label: string;
  query: string;
  removable?: boolean;
}>();

const emit = defineEmits<{
  remove: [];
}>();

const locationQuery = computed(() => props.query);
</script>

<template>
  <article class="bg-surface-card border border-surface-border rounded-xl p-6 md:p-7 font-mono">
    <div class="flex items-start justify-between gap-3 mb-4">
      <h3 class="text-lg font-bold text-surface-light">{{ label }}</h3>
      <button
        v-if="removable"
        type="button"
        class="text-sm text-surface-mid hover:text-accent-golden shrink-0"
        @click="emit('remove')"
      >
        Remove
      </button>
    </div>
    <WeatherSummaryCard :query="locationQuery" />
  </article>
</template>
