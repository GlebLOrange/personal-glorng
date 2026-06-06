<script setup lang="ts">
import { computed, onMounted, watch } from "vue";

import { useWeatherLookup } from "@/composables/useWeatherLookup";
import { DEFAULT_WEATHER_LOCATION } from "@/constants/weather";
import {
  formatLiveLocalTime,
  weatherLocationLabel,
  weatherUtcOffsetHours,
} from "@/utils/weather";

const props = withDefaults(
  defineProps<{
    location?: string;
    compact?: boolean;
    showTime?: boolean;
  }>(),
  {
    location: "",
    compact: false,
    showTime: true,
  },
);

const locationRef = computed(() => props.location.trim() || DEFAULT_WEATHER_LOCATION.query);

const { weather, loading, error, refresh } = useWeatherLookup(locationRef);

const locationLabel = computed(() =>
  weather.value ? weatherLocationLabel(weather.value) : "",
);

const liveTime = computed(() => {
  if (!weather.value || !props.showTime) {
    return null;
  }
  const offset = weatherUtcOffsetHours(weather.value);
  return offset !== null ? formatLiveLocalTime(offset) : null;
});

onMounted(() => {
  if (locationRef.value.trim()) {
    void refresh();
  }
});

watch(locationRef, () => {
  if (locationRef.value.trim()) {
    void refresh();
  }
});
</script>

<template>
  <div v-if="loading" class="text-surface-mid text-sm font-mono animate-pulse">
    Loading weather...
  </div>

  <div v-else-if="error" class="text-sm font-mono space-y-2">
    <p class="text-accent-golden">{{ error }}</p>
    <button type="button" class="text-surface-mid hover:text-surface-light underline" @click="refresh">
      Retry
    </button>
  </div>

  <div v-else-if="weather" class="font-mono">
    <div v-if="compact" class="flex items-center gap-2 text-sm flex-wrap">
      <span class="text-surface-light font-bold">
        {{ locationLabel }}
      </span>
      <template v-if="liveTime">
        <span class="text-surface-muted">·</span>
        <span class="text-surface-mid tabular-nums">{{ liveTime }}</span>
      </template>
      <span class="text-surface-muted">·</span>
      <span class="accent-gradient text-lg font-bold">
        {{ weather.current_condition?.[0]?.temp_C }}°C
      </span>
      <span class="text-surface-muted">·</span>
      <span class="text-surface-mid"> {{ weather.current_condition?.[0]?.humidity }}% </span>
      <span class="text-surface-muted">·</span>
      <span class="text-surface-mid">
        {{ weather.current_condition?.[0]?.weatherDesc?.[0]?.value }}
      </span>
    </div>

    <div v-else class="bg-surface-card border border-surface-border rounded-lg p-6">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Location</div>
          <div class="text-surface-light font-bold">
            {{ locationLabel }}
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
