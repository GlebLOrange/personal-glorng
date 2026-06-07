<script setup lang="ts">
import { computed, onMounted } from "vue";

import { useLiveLocalTime } from "@/composables/useLiveLocalTime";
import { useWeatherConfig } from "@/composables/useWeatherConfig";
import { useWeatherLookup } from "@/composables/useWeatherLookup";
import {
  weatherAnchorUnixtime,
  weatherLocationLabel,
  weatherUtcOffsetHours,
} from "@/utils/weather";

const props = withDefaults(
  defineProps<{
    location?: string;
    compact?: boolean;
    bar?: boolean;
    showTime?: boolean;
  }>(),
  {
    location: "",
    compact: false,
    bar: false,
    showTime: true,
  },
);

const { config, fetchConfig } = useWeatherConfig();

const locationRef = computed(() => props.location.trim() || config.value.query);

const { weather, loading, error, refresh } = useWeatherLookup(locationRef);

const locationLabel = computed(() => (weather.value ? weatherLocationLabel(weather.value) : ""));

const utcOffset = computed(() => {
  if (!weather.value || !props.showTime) {
    return null;
  }
  return weatherUtcOffsetHours(weather.value);
});

const anchorUnixtime = computed(() => {
  if (!weather.value || !props.showTime) {
    return null;
  }
  return weatherAnchorUnixtime(weather.value);
});

const timeFormat = computed((): "time" | "datetime" => (props.bar ? "datetime" : "time"));
const { liveTime, liveDateTime } = useLiveLocalTime(utcOffset, timeFormat, anchorUnixtime);

onMounted(async () => {
  await fetchConfig();
});
</script>

<template>
  <div v-if="loading" class="text-surface-mid text-sm font-mono animate-pulse">
    Loading weather...
  </div>

  <div v-else-if="error" class="text-sm font-mono space-y-2">
    <p class="text-accent-golden">{{ error }}</p>
    <button
      type="button"
      class="text-surface-mid hover:text-surface-light underline"
      @click="refresh"
    >
      Retry
    </button>
  </div>

  <div v-else-if="weather" class="font-mono">
    <div v-if="compact && bar" class="flex items-center gap-3 flex-wrap min-w-0 text-base">
      <span class="text-surface-light font-bold truncate">
        {{ locationLabel }}
      </span>
      <template v-if="liveTime">
        <span class="text-surface-muted">·</span>
        <time
          :datetime="liveDateTime ?? undefined"
          class="shrink-0 text-sm sm:text-base font-bold text-surface-light"
        >
          {{ liveTime }}
        </time>
      </template>
      <span class="text-surface-muted">·</span>
      <span class="font-bold accent-gradient text-xl tabular-nums">
        {{ weather.current_condition?.[0]?.temp_C }}°C
      </span>
      <span class="inline-flex items-center gap-1 text-surface-mid shrink-0">
        <svg
          aria-hidden="true"
          class="w-4 h-4 text-accent-blue"
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path
            d="M12 2.69c-1.46 2.05-3.62 3.88-3.62 6.31a3.62 3.62 0 0 0 7.24 0c0-2.43-2.16-4.26-3.62-6.31zm0 14.5c-3.31 0-6 2.24-6 5a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1c0-2.76-2.69-5-6-5z"
          />
        </svg>
        <span>{{ weather.current_condition?.[0]?.humidity }}%</span>
      </span>
      <span class="inline-flex items-center gap-1 text-surface-mid shrink-0">
        <svg
          aria-hidden="true"
          class="w-4 h-4 text-accent-violet"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        >
          <path d="M3 8c2-2 4-1 6 1s4 2 6 0 4-2 6 1" />
          <path d="M3 14c2-2 4-1 6 1s4 2 6 0 4-2 6 1" />
        </svg>
        <span>{{ weather.current_condition?.[0]?.windspeedKmph }} km/h</span>
      </span>
    </div>

    <div v-else-if="compact" class="flex items-center gap-2 flex-wrap min-w-0 text-sm">
      <span class="text-surface-light font-bold truncate">
        {{ locationLabel }}
      </span>
      <template v-if="liveTime">
        <span class="text-surface-muted">·</span>
        <span class="text-surface-mid tabular-nums shrink-0">{{ liveTime }}</span>
      </template>
      <span class="text-surface-muted">·</span>
      <span class="font-bold accent-gradient text-lg">
        {{ weather.current_condition?.[0]?.temp_C }}°C
      </span>
      <span class="text-surface-muted">·</span>
      <span class="text-surface-mid">{{ weather.current_condition?.[0]?.humidity }}%</span>
      <span class="text-surface-muted">·</span>
      <span class="text-surface-mid truncate">
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

  <div v-else class="text-sm font-mono text-surface-mid">
    Weather unavailable.
    <button type="button" class="ml-2 underline hover:text-surface-light" @click="refresh">
      Retry
    </button>
  </div>
</template>
