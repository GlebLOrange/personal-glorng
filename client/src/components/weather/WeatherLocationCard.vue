<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import { useWeatherLookup } from "@/composables/useWeatherLookup";
import {
  formatLiveLocalTime,
  weatherLocationLabel,
  weatherObservedTime,
  weatherUtcOffsetHours,
} from "@/utils/weather";

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

const liveTime = ref<string | null>(null);
let timer: ReturnType<typeof setInterval> | null = null;

function updateLiveTime(): void {
  if (!weather.value) {
    liveTime.value = null;
    return;
  }
  const offset = weatherUtcOffsetHours(weather.value);
  liveTime.value = offset !== null ? formatLiveLocalTime(offset) : weatherObservedTime(weather.value);
}

onMounted(() => {
  void refresh();
  updateLiveTime();
  timer = setInterval(updateLiveTime, 30_000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});

watch(weather, () => {
  updateLiveTime();
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

    <div v-else-if="weather" class="flex items-end justify-between gap-4">
      <div>
        <p v-if="liveTime" class="text-3xl font-bold text-surface-light tabular-nums">
          {{ liveTime }}
        </p>
        <p class="text-xs text-surface-mid mt-1">local time</p>
      </div>
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
