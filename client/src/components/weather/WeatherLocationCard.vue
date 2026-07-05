<script setup lang="ts">
import { computed } from "vue";

import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import WeatherSummaryContent from "@/components/weather/WeatherSummaryContent.vue";

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
  <Card as="article" class="font-mono">
    <CardHeader>
      <CardTitle as="h3">{{ label }}</CardTitle>
      <template #actions>
        <button
          v-if="removable"
          type="button"
          class="text-sm text-surface-mid hover:text-accent-golden shrink-0"
          @click="emit('remove')"
        >
          Remove
        </button>
      </template>
    </CardHeader>
    <WeatherSummaryContent :query="locationQuery" />
  </Card>
</template>
