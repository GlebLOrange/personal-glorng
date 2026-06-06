<script setup lang="ts">
import { computed, onMounted, watch } from "vue";

import CityAnalogClock from "@/components/weather/CityAnalogClock.vue";
import { useWeatherLookup } from "@/composables/useWeatherLookup";
import { weatherLocationLabel, weatherUtcOffsetHours } from "@/utils/weather";

const props = defineProps<{
  label: string;
  query: string;
  removable?: boolean;
}>();

const emit = defineEmits<{
  remove: [];
}>();

const locationRef = computed(() => props.query);
const { weather, loading, error, refresh } = useWeatherLookup(locationRef);

const utcOffset = computed(() =>
  weather.value ? weatherUtcOffsetHours(weather.value) : null,
);

onMounted(() => {
  void refresh();
});

watch(locationRef, () => {
  if (locationRef.value.trim()) {
    void refresh();
  }
});
</script>

<template>
  <article class="bg-surface-card border border-surface-border rounded-xl p-6 md:p-7 font-mono">
    <div class="flex items-start justify-between gap-3 mb-5">
      <div>
        <h3 class="text-lg font-bold text-surface-light">{{ label }}</h3>
        <p v-if="weather" class="text-sm text-surface-mid mt-1">
          {{ weatherLocationLabel(weather) }}
        </p>
      </div>
      <button
        v-if="removable"
        type="button"
        class="text-sm text-surface-mid hover:text-accent-golden"
        @click="emit('remove')"
      >
        Remove
      </button>
    </div>

    <div v-if="loading" class="text-base text-surface-mid animate-pulse py-4">Loading...</div>

    <div v-else-if="error" class="text-base space-y-2">
      <p class="text-accent-golden">{{ error }}</p>
      <button type="button" class="text-surface-mid underline" @click="refresh">Retry</button>
    </div>

    <div v-else-if="weather" class="flex items-center justify-between gap-6">
      <CityAnalogClock :utc-offset-hours="utcOffset" :size="128" />
      <div class="text-right">
        <p class="text-4xl md:text-5xl font-bold accent-gradient tabular-nums">
          {{ weather.current_condition?.[0]?.temp_C }}°C
        </p>
        <p class="text-sm text-surface-mid mt-2 max-w-[12rem] ml-auto">
          {{ weather.current_condition?.[0]?.weatherDesc?.[0]?.value }}
        </p>
        <p class="text-xs text-surface-muted mt-1">
          {{ weather.current_condition?.[0]?.humidity }}% humidity
        </p>
      </div>
    </div>
  </article>
</template>
