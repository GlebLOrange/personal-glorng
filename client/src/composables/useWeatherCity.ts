import { ref, type Ref } from "vue";

const STORAGE_KEY = "admin-weather-city";
const DEFAULT_CITY = "Wroclaw";

function readStoredCity(): string {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)?.trim();
    return stored || DEFAULT_CITY;
  } catch {
    return DEFAULT_CITY;
  }
}

const weatherCity = ref(readStoredCity());

/** Persisted admin weather city (shared by dashboard widget and weather tool). */
export function useWeatherCity(): {
  weatherCity: Ref<string>;
  setWeatherCity: (city: string) => void;
} {
  function setWeatherCity(city: string): void {
    const trimmed = city.trim();
    if (!trimmed) return;
    weatherCity.value = trimmed;
    try {
      localStorage.setItem(STORAGE_KEY, trimmed);
    } catch {
      // ignore quota / private mode
    }
  }

  return { weatherCity, setWeatherCity };
}
