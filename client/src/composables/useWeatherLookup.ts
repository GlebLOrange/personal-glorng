import { computed, ref, type ComputedRef, type Ref } from "vue";

import { useCachedApi } from "@/composables/useCachedApi";
import type { WeatherData } from "@/types";

import {
  TIME_DATE_WEATHER_LOCATION_API_PREFIX,
} from "@/constants/timeDateWeatherLocation";

/** Build the public lookup API path for a city or lat,lon pair. */
export function weatherLookupUrl(location: string): string {
  return `${TIME_DATE_WEATHER_LOCATION_API_PREFIX}/lookup/${encodeURIComponent(location.trim())}`;
}

/** Fetch weather for a single city or coordinate pair. */
export function useWeatherLookup(location: ComputedRef<string>): {
  weather: Ref<WeatherData | null>;
  loading: ComputedRef<boolean>;
  error: Ref<string | null>;
  refresh: () => Promise<void>;
} {
  const url = computed(() => {
    const value = location.value.trim();
    return value ? weatherLookupUrl(value) : "";
  });

  const { data, loading, fetch } = useCachedApi<WeatherData>(url);
  const error = ref<string | null>(null);

  async function refresh(): Promise<void> {
    if (!location.value.trim()) {
      return;
    }
    error.value = null;
    try {
      await fetch();
    } catch {
      error.value = "Couldn't load weather";
    }
  }

  return {
    weather: data,
    loading: computed(() => loading.value && Boolean(location.value.trim())),
    error,
    refresh,
  };
}
