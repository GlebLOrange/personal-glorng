<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import { useCachedApi } from "@/composables/useCachedApi";
import { useSiteWeather } from "@/composables/useSiteWeather";
import type { WeatherData } from "@/types";
import { weatherLocationLabel } from "@/utils/weather";

const props = withDefaults(
  defineProps<{
    previewCity?: string;
    compact?: boolean;
  }>(),
  { previewCity: undefined, compact: false },
);

const siteWeather = useSiteWeather();
const previewError = ref<string | null>(null);

const previewUrl = computed(() =>
  props.previewCity
    ? `/tools/weather/${encodeURIComponent(props.previewCity)}`
    : "",
);

const {
  data: previewWeather,
  loading: previewLoading,
  fetch: fetchPreview,
} = useCachedApi<WeatherData>(previewUrl);

const isPreview = computed(() => Boolean(props.previewCity?.trim()));

const weather = computed(() =>
  isPreview.value ? previewWeather.value : siteWeather.weather.value,
);

const loading = computed(() =>
  isPreview.value ? previewLoading.value : siteWeather.loading.value,
);

const error = computed(() =>
  isPreview.value ? previewError.value : siteWeather.error.value,
);

const locationLabel = computed(() =>
  weather.value ? weatherLocationLabel(weather.value) : "",
);

async function loadPreview(): Promise<void> {
  if (!props.previewCity?.trim()) {
    return;
  }
  previewError.value = null;
  try {
    await fetchPreview();
  } catch {
    previewError.value = "Couldn't load weather preview";
  }
}

async function retry(): Promise<void> {
  if (isPreview.value) {
    await loadPreview();
    return;
  }
  await siteWeather.refresh();
}

onMounted(() => {
  if (isPreview.value) {
    void loadPreview();
    return;
  }
  void siteWeather.refresh();
});

watch(
  () => props.previewCity,
  () => {
    if (isPreview.value) {
      void loadPreview();
    }
  },
);
</script>

<template>
  <div v-if="loading" class="text-surface-mid text-sm font-mono animate-pulse">
    Loading weather...
  </div>

  <div v-else-if="error" class="text-sm font-mono space-y-2">
    <p class="text-accent-golden">{{ error }}</p>
    <button type="button" class="text-surface-mid hover:text-surface-light underline" @click="retry">
      Retry
    </button>
  </div>

  <div v-else-if="weather" class="font-mono">
    <div v-if="compact" class="flex items-center gap-2 text-sm flex-wrap">
      <span class="text-surface-light font-bold">
        {{ locationLabel }}
      </span>
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
