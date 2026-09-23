<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import ToastContainer from "@/components/ui/ToastContainer.vue";
import WeatherBar from "@/components/weather/WeatherBar.vue";
import { WEATHER_ROUTE_NAME } from "@/constants/weather";

/** Weather/toast strip only on tools hub + public utility routes — not news/settings/admin. */
const PINNED_TOOLS_ROUTE_NAMES = new Set<string>([
  "tools",
  WEATHER_ROUTE_NAME,
  "calculator",
  "expense-calculator",
  "password-generator",
  "recipes",
  "shortener",
  "vid-download",
  "tool-health-checker",
]);

const route = useRoute();
const showPinnedRow = computed(() => {
  const name = route.name;
  return typeof name === "string" && PINNED_TOOLS_ROUTE_NAMES.has(name);
});
</script>

<template>
  <div v-if="showPinnedRow" class="page-tool-grid mb-8 min-w-0">
    <ToastContainer variant="tile" />
    <WeatherBar wrapper-class="page-tile md:col-start-3" card-class="page-weather-tile-card" />
  </div>
</template>
