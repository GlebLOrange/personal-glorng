import { computed, type ComputedRef, type Ref } from "vue";

import { useLocalStorageString } from "@/composables/useLocalStorage";
import { useWeatherConfig } from "@/composables/useWeatherConfig";
import { useWeatherLocations } from "@/composables/useWeatherLocations";
import { ACTIVE_WEATHER_QUERY_KEY } from "@/constants/weather";

/** Active city query for header weather: localStorage with saved-city fallback. */
export function useActiveWeatherQuery(): {
  activeQuery: ComputedRef<string>;
  setActiveQuery: (query: string) => void;
  storedQuery: Ref<string>;
} {
  const { config } = useWeatherConfig();
  const { locations, isDefaultLocation, setGuestDefaultByQuery } = useWeatherLocations();
  const { value: storedQuery, set: setStoredQuery } = useLocalStorageString(
    ACTIVE_WEATHER_QUERY_KEY,
    "",
  );

  const activeQuery = computed(() => {
    const stored = storedQuery.value.trim();
    if (
      stored &&
      locations.value.some((loc) => loc.query.toLowerCase() === stored.toLowerCase())
    ) {
      return stored;
    }

    const defaultLoc = locations.value.find((loc) => isDefaultLocation(loc));
    if (defaultLoc) {
      return defaultLoc.query;
    }

    return config.value.query;
  });

  function setActiveQuery(query: string): void {
    const trimmed = query.trim();
    if (!trimmed) {
      return;
    }
    setStoredQuery(trimmed);
    setGuestDefaultByQuery(trimmed);
  }

  return { activeQuery, setActiveQuery, storedQuery };
}
