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
    query?: string;
    interactive?: boolean;
  }>(),
  {
    query: "",
    interactive: false,
  },
);

const { config, fetchConfig } = useWeatherConfig();

const locationRef = computed(() => props.query.trim() || config.value.query);

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

const utcOffset = computed(() => (weather.value ? weatherUtcOffsetHours(weather.value) : null));

const anchorUnixtime = computed(() =>
  weather.value ? weatherAnchorUnixtime(weather.value) : null,
);

const { liveTime, liveDate, liveDateTime, liveDateIso } = useLiveLocalTime(
  utcOffset,
  computed(() => "time" as const),
  anchorUnixtime,
);

onMounted(async () => {
  await fetchConfig();
});
</script>

<template>
  <div
    class="font-mono min-w-0"
    :class="interactive ? 'rounded-lg transition-colors' : undefined"
  >
    <div v-if="loading" class="space-y-1.5 animate-pulse" aria-busy="true">
      <div class="h-8 w-24 rounded bg-surface-border/60" />
      <div class="h-4 w-28 rounded bg-surface-border/40" />
      <div class="h-4 w-40 rounded bg-surface-border/40" />
    </div>

    <div v-else-if="error" class="text-sm space-y-2">
      <p class="text-accent-golden">{{ error }}</p>
      <button
        type="button"
        class="text-surface-mid hover:text-surface-light underline"
        @click="refresh"
      >
        Retry
      </button>
    </div>

    <div
      v-else-if="weather"
      class="flex flex-col gap-0.5 min-w-0"
      :aria-label="liveTime ? `Local time ${liveTime}` : undefined"
    >
      <time
        v-if="liveTime"
        :datetime="liveDateTime ?? undefined"
        class="text-2xl sm:text-3xl font-bold text-surface-light tabular-nums tracking-tight"
        role="timer"
      >
        {{ liveTime }}
      </time>
      <time
        v-if="liveDate"
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

    <div v-else class="text-sm text-surface-mid">
      Weather unavailable.
      <button type="button" class="ml-2 underline hover:text-surface-light" @click="refresh">
        Retry
      </button>
    </div>
  </div>
</template>
