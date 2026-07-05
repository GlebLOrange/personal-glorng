<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import WeatherSummaryCard from "@/components/weather/WeatherSummaryCard.vue";
import { WEATHER_PATH, WEATHER_ROUTE_NAME, WEATHER_TOOL_NAME } from "@/constants/weather";

const route = useRoute();

const visible = computed(() => route.name !== WEATHER_ROUTE_NAME);
</script>

<template>
  <aside v-if="visible" :aria-label="WEATHER_TOOL_NAME" class="w-full border-b border-surface-border">
    <RouterLink
      :to="WEATHER_PATH"
      class="interactive-surface block w-full px-4 py-3 sm:py-4 rounded-none border-0 hover:border-accent-blue/40 transition-colors"
    >
      <div class="max-w-5xl mx-auto min-w-0">
        <WeatherSummaryCard interactive class="min-w-0" />
      </div>
    </RouterLink>
  </aside>
</template>
