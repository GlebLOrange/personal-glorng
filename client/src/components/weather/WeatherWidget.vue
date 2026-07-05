<script setup lang="ts">
import { computed, onMounted } from "vue";

import { useLiveLocalTime } from "@/composables/useLiveLocalTime";
import { useWeatherConfig } from "@/composables/useWeatherConfig";
import { useWeatherLookup } from "@/composables/useWeatherLookup";
import {
  weatherAnchorUnixtime,
  weatherConditionEmoji,
  weatherLocationLabel,
  weatherUtcOffsetHours,
} from "@/utils/weather";

const props = withDefaults(
  defineProps<{
    location?: string;
    compact?: boolean;
    stack?: boolean;
    showTime?: boolean;
  }>(),
  {
    location: "",
    compact: false,
    stack: false,
    showTime: true,
  },
);

const { config, fetchConfig } = useWeatherConfig();

const locationRef = computed(() => props.location.trim() || config.value.query);

const { weather, loading, error, refresh } = useWeatherLookup(locationRef);

const locationLabel = computed(() => (weather.value ? weatherLocationLabel(weather.value) : ""));

const currentCondition = computed(() => weather.value?.current_condition?.[0]);

const temperature = computed(() => currentCondition.value?.temp_C ?? "—");

const conditionText = computed(() => currentCondition.value?.weatherDesc?.[0]?.value ?? "");

const weatherEmoji = computed(() =>
  weatherConditionEmoji(currentCondition.value?.weatherCode, conditionText.value),
);

const conditionsAriaLabel = computed(() => {
  const parts = [`${temperature.value} degrees Celsius`, locationLabel.value];
  if (conditionText.value) {
    parts.push(conditionText.value);
  }
  return parts.join(", ");
});

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

const timeFormat = computed((): "time" | "datetime" => (props.stack ? "time" : "datetime"));
const { liveTime, liveDate, liveDateTime, liveDateIso } = useLiveLocalTime(
  utcOffset,
  timeFormat,
  anchorUnixtime,
);

onMounted(async () => {
  await fetchConfig();
});
</script>

<template>
  <div v-if="loading" class="font-mono space-y-1.5 animate-pulse" aria-busy="true">
    <div class="h-8 w-24 rounded bg-surface-border/60" />
    <div class="h-4 w-28 rounded bg-surface-border/40" />
    <div class="h-4 w-40 rounded bg-surface-border/40" />
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
    <div
      v-if="compact && stack"
      class="flex flex-col gap-0.5 min-w-0"
      :aria-label="showTime && liveTime ? `Local time ${liveTime}` : undefined"
    >
      <time
        v-if="showTime && liveTime"
        :datetime="liveDateTime ?? undefined"
        class="text-2xl sm:text-3xl font-bold text-surface-light tabular-nums tracking-tight"
        role="timer"
      >
        {{ liveTime }}
      </time>
      <time
        v-if="showTime && liveDate"
        :datetime="liveDateIso ?? undefined"
        class="text-sm text-surface-mid"
      >
        {{ liveDate }}
      </time>
      <p
        class="flex items-center gap-1.5 min-w-0 text-sm text-surface-mid"
        :aria-label="conditionsAriaLabel"
      >
        <span aria-hidden="true">{{ weatherEmoji }}</span>
        <span class="font-bold accent-gradient tabular-nums shrink-0">{{ temperature }}°C</span>
        <span aria-hidden="true" class="text-surface-muted">·</span>
        <span class="truncate text-surface-light">{{ locationLabel }}</span>
        <span v-if="conditionText" class="sr-only">{{ conditionText }}</span>
      </p>
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
            {{ temperature }}°C
          </div>
        </div>
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Condition</div>
          <div class="text-surface-light">
            {{ conditionText }}
          </div>
        </div>
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Humidity / Wind</div>
          <div class="text-surface-light text-sm">
            {{ currentCondition?.humidity }}% /
            {{ currentCondition?.windspeedKmph }} km/h
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
