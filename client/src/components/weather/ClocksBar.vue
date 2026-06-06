<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import WeatherWidget from "@/components/weather/WeatherWidget.vue";
import {
  DATE_TIME_LOCATION_SECTION,
  TIME_DATE_WEATHER_LOCATION_PATH,
  TIME_DATE_WEATHER_LOCATION_ROUTE_NAME,
} from "@/constants/timeDateWeatherLocation";

const route = useRoute();

const visible = computed(() => route.name !== TIME_DATE_WEATHER_LOCATION_ROUTE_NAME);
</script>

<template>
  <aside
    v-if="visible"
    :aria-label="DATE_TIME_LOCATION_SECTION"
    class="w-full border-b border-surface-border"
  >
    <RouterLink
      :to="TIME_DATE_WEATHER_LOCATION_PATH"
      class="interactive-surface block w-full px-4 py-3.5 rounded-none border-0 hover:border-accent-blue/40 transition-colors"
    >
      <div class="max-w-5xl mx-auto flex items-center justify-between gap-4 min-w-0">
        <WeatherWidget compact bar show-time class="min-w-0 flex-1" />
        <span class="text-sm text-surface-mid shrink-0 font-mono">{{ DATE_TIME_LOCATION_SECTION }} →</span>
      </div>
    </RouterLink>
  </aside>
</template>
