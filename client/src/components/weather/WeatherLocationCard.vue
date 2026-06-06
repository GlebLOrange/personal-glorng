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
  <article class="bg-surface-card border border-surface-border rounded-lg p-5 font-mono">
    <div class="flex items-start justify-between gap-3 mb-4">
      <div>
        <h3 class="text-surface-light font-bold">{{ label }}</h3>
        <p v-if="weather" class="text-xs text-surface-mid mt-1">
          {{ weatherLocationLabel(weather) }}
        </p>
      </div>
      <button
        v-if="removable"
        type="button"
        class="text-xs text-surface-mid hover:text-accent-golden"
        @click="emit('remove')"
      >
        Remove
      </button>
    </div>

    <div v-if="loading" class="text-sm text-surface-mid animate-pulse">Loading...</div>

    <div v-else-if="error" class="text-sm space-y-2">
      <p class="text-accent-golden">{{ error }}</p>
      <button type="button" class="text-surface-mid underline" @click="refresh">Retry</button>
    </div>

    <div v-else-if="weather" class="flex items-center justify-between gap-4">
      <CityAnalogClock :utc-offset-hours="utcOffset" />
      <div class="text-right">
        <p class="text-3xl font-bold accent-gradient">
          {{ weather.current_condition?.[0]?.temp_C }}°C
        </p>
        <p class="text-xs text-surface-mid mt-1">
          {{ weather.current_condition?.[0]?.weatherDesc?.[0]?.value }}
        </p>
      </div>
    </div>
  </article>
</template>
