import { ref, type Ref } from "vue";

import { api } from "@/composables/useApi";
import {
  DEFAULT_WEATHER_LOCATION,
  WEATHER_API_PREFIX,
} from "@/constants/weather";
import type { WeatherConfig } from "@/types";

const config = ref<WeatherConfig>({ ...DEFAULT_WEATHER_LOCATION });
const loaded = ref(false);
let loadPromise: Promise<void> | null = null;

/** Shared weather default city config from the server with offline fallback. */
export function useWeatherConfig(): {
  config: Ref<WeatherConfig>;
  loaded: Ref<boolean>;
  fetchConfig: () => Promise<WeatherConfig>;
  isDefaultQuery: (query: string) => boolean;
} {
  async function fetchConfig(): Promise<WeatherConfig> {
    if (loaded.value) {
      return config.value;
    }
    if (!loadPromise) {
      loadPromise = (async () => {
        try {
          const { data } = await api.get<WeatherConfig>(
            `${WEATHER_API_PREFIX}/config`,
          );
          config.value = data;
        } catch {
          config.value = { ...DEFAULT_WEATHER_LOCATION };
        } finally {
          loaded.value = true;
        }
      })();
    }
    await loadPromise;
    return config.value;
  }

  function isDefaultQuery(query: string): boolean {
    return query.trim().toLowerCase() === config.value.query.toLowerCase();
  }

  return { config, loaded, fetchConfig, isDefaultQuery };
}
