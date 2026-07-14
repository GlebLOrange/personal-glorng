<script setup lang="ts">
import { Card } from "@/components/ui/card";
import WeatherSummaryContent from "@/components/weather/WeatherSummaryContent.vue";

defineProps<{
  label: string;
  query: string;
  removable?: boolean;
}>();

const emit = defineEmits<{
  select: [];
  remove: [];
}>();

function handleRemove(event: MouseEvent): void {
  event.stopPropagation();
  emit("remove");
}
</script>

<template>
  <div class="page-tile relative h-full min-w-0 w-full">
    <button
      type="button"
      class="block h-full min-w-0 w-full text-left"
      :aria-label="`Set ${label} as active city`"
      @click="emit('select')"
    >
      <Card hoverable class="page-weather-tile-card h-full">
        <WeatherSummaryContent :query="query" align="center" dense interactive />
      </Card>
    </button>
    <button
      v-if="removable"
      type="button"
      class="absolute right-3 top-3 text-xs text-surface-mid hover:text-accent-golden"
      :aria-label="`Remove ${label}`"
      @click="handleRemove"
    >
      Remove
    </button>
  </div>
</template>
