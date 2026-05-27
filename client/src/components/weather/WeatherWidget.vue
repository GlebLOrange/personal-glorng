<script setup lang="ts">
import { onMounted } from "vue";

import { useCachedApi } from "@/composables/useCachedApi";
import type { WeatherData } from "@/types";

const props = withDefaults(
  defineProps<{
    city?: string;
    compact?: boolean;
  }>(),
  { city: "Wroclaw", compact: false },
);

const url = `/tools/weather/${encodeURIComponent(props.city)}`;
const { data: weather, loading, fetch: fetchWeather } = useCachedApi<WeatherData>(url);

onMounted(fetchWeather);
</script>

<template>
  <div v-if="loading" class="text-surface-mid text-sm font-mono animate-pulse">
    Loading weather...
  </div>

  <div v-else-if="weather" class="font-mono">
    <div v-if="compact" class="flex items-center gap-3 text-sm">
      <span class="text-surface-light font-bold">
        {{ weather.nearest_area?.[0]?.areaName?.[0]?.value }}
      </span>
      <span class="accent-gradient text-lg font-bold">
        {{ weather.current_condition?.[0]?.temp_C }}°C
      </span>
      <span class="text-surface-mid">
        {{ weather.current_condition?.[0]?.weatherDesc?.[0]?.value }}
      </span>
    </div>

    <div v-else class="bg-surface-card border border-surface-border rounded-lg p-6">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Location</div>
          <div class="text-surface-light font-bold">
            {{ weather.nearest_area?.[0]?.areaName?.[0]?.value }},
            {{ weather.nearest_area?.[0]?.country?.[0]?.value }}
          </div>
        </div>
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Temperature</div>
          <div class="text-3xl font-bold accent-gradient">
            {{ weather.current_condition?.[0]?.temp_C }}°C
          </div>
        </div>
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Condition</div>
          <div class="text-surface-light">
            {{ weather.current_condition?.[0]?.weatherDesc?.[0]?.value }}
          </div>
        </div>
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Humidity / Wind</div>
          <div class="text-surface-light text-sm">
            {{ weather.current_condition?.[0]?.humidity }}% /
            {{ weather.current_condition?.[0]?.windspeedKmph }} km/h
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
