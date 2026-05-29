import { useLocalStorageString } from "@/composables/useLocalStorage";

const STORAGE_KEY = "admin-weather-city";
const DEFAULT_CITY = "Wroclaw";

const { value: weatherCity, set: setWeatherCity } = useLocalStorageString(
  STORAGE_KEY,
  DEFAULT_CITY,
);

/** Persisted admin weather city (shared by tools page widget and weather tool). */
export function useWeatherCity(): {
  weatherCity: typeof weatherCity;
  setWeatherCity: (city: string) => void;
} {
  return { weatherCity, setWeatherCity };
}
