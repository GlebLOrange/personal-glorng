<script setup lang="ts">
import { Card } from "@/components/ui/card";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import WeatherSummaryContent from "@/components/weather/WeatherSummaryContent.vue";

defineProps<{
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
      :aria-label="`Set ${query} as active city`"
      @click="emit('select')"
    >
      <Card hoverable class="page-weather-tile-card h-full">
        <WeatherSummaryContent :query="query" align="center" dense interactive />
      </Card>
    </button>
    <IconCloseButton
      v-if="removable"
      class="absolute right-2 top-2 z-10"
      :aria-label="`Remove ${query}`"
      @click="handleRemove"
    />
  </div>
</template>
