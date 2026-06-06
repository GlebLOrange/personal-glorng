import { computed, ref, type ComputedRef, type Ref } from "vue";

import { api } from "@/composables/useApi";
import { invalidateCachedApi, useCachedApi } from "@/composables/useCachedApi";
import type { WeatherConfig, WeatherData } from "@/types";

const CONFIG_URL = "/weather/config";
const CURRENT_URL = "/weather/current";

const configApi = useCachedApi<WeatherConfig>(CONFIG_URL);
const currentApi = useCachedApi<WeatherData>(CURRENT_URL);

const saving = ref(false);
const error = ref<string | null>(null);

const displayCity: ComputedRef<string | null> = computed(
  () => configApi.data.value?.city ?? null,
);

const weather: Ref<WeatherData | null> = currentApi.data;

const loading = computed(() => configApi.loading.value || currentApi.loading.value);

async function refresh(): Promise<void> {
  error.value = null;
  try {
    await Promise.all([configApi.fetch(), currentApi.fetch()]);
  } catch {
    error.value = "Couldn't load weather";
  }
}

async function setDisplayCity(city: string): Promise<void> {
  const trimmed = city.trim();
  if (!trimmed) {
    return;
  }

  saving.value = true;
  error.value = null;
  try {
    await api.put<WeatherConfig>("/tools/weather/city", { city: trimmed });
    invalidateCachedApi(CONFIG_URL);
    invalidateCachedApi(CURRENT_URL);
    await Promise.all([configApi.fetch(), currentApi.fetch()]);
  } catch {
    error.value = "Failed to update city";
    throw new Error("Failed to update city");
  } finally {
    saving.value = false;
  }
}

/** Site-wide weather state shared across portfolio and admin surfaces. */
export function useSiteWeather(): {
  displayCity: ComputedRef<string | null>;
  weather: Ref<WeatherData | null>;
  loading: ComputedRef<boolean>;
  saving: Ref<boolean>;
  error: Ref<string | null>;
  refresh: () => Promise<void>;
  setDisplayCity: (city: string) => Promise<void>;
} {
  return {
    displayCity,
    weather,
    loading,
    saving,
    error,
    refresh,
    setDisplayCity,
  };
}
