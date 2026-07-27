<script setup lang="ts">
import { computed, onMounted } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import LocationIcon from "@/components/icons/LocationIcon.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import WeatherConditionIcon from "@/components/weather/WeatherConditionIcon.vue";
import { useLiveLocalTime } from "@/composables/useLiveLocalTime";
import { useWeatherConfig } from "@/composables/useWeatherConfig";
import { useWeatherLookup } from "@/composables/useWeatherLookup";
import {
  weatherConditionKind,
  weatherIanaTimezone,
  weatherLocationLabel,
  weatherUtcOffsetHours,
} from "@/utils/weather";

const props = withDefaults(
  defineProps<{
    query?: string;
    interactive?: boolean;
    align?: "left" | "center" | "right";
    dense?: boolean;
    size?: "default" | "chrome";
  }>(),
  {
    query: "",
    interactive: false,
    align: "left",
    dense: false,
    size: "default",
  },
);

const isRight = computed(() => props.align === "right");
const isCenter = computed(() => props.align === "center");

const stackClass = computed(() => {
  if (isCenter.value) return "items-center text-center";
  if (isRight.value) return "items-end text-right";
  return "items-start text-left";
});

const skeletonClass = computed(() => {
  if (isCenter.value || isRight.value) return "mx-auto";
  return undefined;
});

const timeClass = computed(() => {
  if (props.size === "chrome") {
    return "text-lg font-bold leading-none text-surface-light tabular-nums tracking-tight";
  }
  if (props.dense) {
    return "text-2xl font-bold text-surface-light tabular-nums tracking-tight";
  }
  return "text-2xl sm:text-3xl font-bold text-surface-light tabular-nums tracking-tight";
});

const dateClass = computed(() =>
  props.size === "chrome" ? "text-xs leading-none text-surface-mid" : "text-sm text-surface-mid",
);

const conditionsClass = computed(() => {
  const base =
    props.size === "chrome"
      ? "flex w-full max-w-full items-center gap-1 min-w-0 text-xs leading-none text-surface-mid"
      : "flex items-center gap-1.5 min-w-0 text-sm text-surface-mid";
  if (isCenter.value) return `${base} justify-center`;
  if (isRight.value) return `${base} justify-end`;
  return base;
});

const rootClass = computed(() => [
  "font-data min-w-0",
  props.size === "chrome" && "w-full max-w-full",
  props.interactive && "rounded-lg transition-colors",
]);

const { config, fetchConfig } = useWeatherConfig();

const locationRef = computed(() => props.query.trim() || config.value.query);

const { weather, loading, error, refresh } = useWeatherLookup(locationRef);

const locationLabel = computed(() => (weather.value ? weatherLocationLabel(weather.value) : ""));

const currentCondition = computed(() => weather.value?.current_condition?.[0]);

const temperature = computed(() => currentCondition.value?.temp_C ?? "—");

const conditionText = computed(() => currentCondition.value?.weatherDesc?.[0]?.value ?? "");

const weatherKind = computed(() =>
  weatherConditionKind(currentCondition.value?.weatherCode, conditionText.value),
);

const conditionsAriaLabel = computed(() => {
  const parts = [`${temperature.value} degrees Celsius`, locationLabel.value];
  if (conditionText.value) {
    parts.push(conditionText.value);
  }
  return parts.join(", ");
});

const utcOffset = computed(() => (weather.value ? weatherUtcOffsetHours(weather.value) : null));

const ianaTimezone = computed(() => (weather.value ? weatherIanaTimezone(weather.value) : null));

const { liveTime, liveDate, liveDateTime, liveDateIso } = useLiveLocalTime(
  utcOffset,
  computed(() => "time" as const),
  ianaTimezone,
);

onMounted(async () => {
  await fetchConfig();
});
</script>

<template>
  <div :class="rootClass">
    <div v-if="loading" class="space-y-1.5 animate-pulse" :class="stackClass" aria-busy="true">
      <div class="h-8 w-24 rounded bg-surface-border/60" :class="skeletonClass" />
      <div class="h-4 w-28 rounded bg-surface-border/40" :class="skeletonClass" />
      <div class="h-4 w-40 rounded bg-surface-border/40" :class="skeletonClass" />
    </div>

    <div v-else-if="error" class="text-sm space-y-2" :class="stackClass">
      <p class="text-status-error">{{ error }}</p>
      <BaseButton variant="ghost" size="sm" class="gap-1.5" @click="refresh">
        <RefreshIcon class-name="size-3.5" />
        retry
      </BaseButton>
    </div>

    <div
      v-else-if="weather"
      class="flex w-full max-w-full flex-col gap-0.5 min-w-0"
      :class="stackClass"
      :aria-label="liveTime ? `local time ${liveTime}` : undefined"
    >
      <time v-if="liveTime" :datetime="liveDateTime ?? undefined" :class="timeClass" role="timer">
        {{ liveTime }}
      </time>
      <time v-if="liveDate" :datetime="liveDateIso ?? undefined" :class="dateClass">
        {{ liveDate }}
      </time>
      <p :class="conditionsClass" :aria-label="conditionsAriaLabel">
        <WeatherConditionIcon :kind="weatherKind" class-name="size-4 inline-block align-[-0.125em]" />
        <span class="font-bold font-data text-accent-blue tabular-nums shrink-0">{{ temperature }}°C</span>
        <span aria-hidden="true" class="text-surface-muted">·</span>
        <span class="inline-flex min-w-0 items-center gap-1 truncate text-surface-light">
          <LocationIcon class-name="size-3.5 shrink-0" />
          <span class="truncate">{{ locationLabel }}</span>
        </span>
        <span v-if="conditionText" class="sr-only">{{ conditionText }}</span>
      </p>
    </div>

    <div v-else class="flex flex-wrap items-center gap-2 text-sm text-surface-mid" :class="stackClass">
      weather unavailable.
      <BaseButton variant="ghost" size="sm" class="gap-1.5" @click="refresh">
        <RefreshIcon class-name="size-3.5" />
        retry
      </BaseButton>
    </div>
  </div>
</template>
