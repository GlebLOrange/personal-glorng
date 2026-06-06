import { computed, ref, watch, type ComputedRef, type Ref } from "vue";

import { api } from "@/composables/useApi";
import { useLocalStorage } from "@/composables/useLocalStorage";
import { useWeatherConfig } from "@/composables/useWeatherConfig";
import {
  LEGACY_SAVED_LOCATIONS_STORAGE_KEY,
  SAVED_LOCATIONS_STORAGE_KEY,
  TIME_DATE_WEATHER_LOCATION_API_PREFIX,
} from "@/constants/timeDateWeatherLocation";
import { useAuthStore } from "@/stores/auth";
import type { WeatherLocation } from "@/types";

export interface GuestWeatherLocation {
  id: string;
  label: string;
  query: string;
  sort_order: number;
  is_default?: boolean;
}

function guestId(): string {
  return crypto.randomUUID();
}

function migrateLegacyGuestLocations(): void {
  if (typeof localStorage === "undefined") {
    return;
  }
  if (localStorage.getItem(SAVED_LOCATIONS_STORAGE_KEY)) {
    return;
  }
  const legacy = localStorage.getItem(LEGACY_SAVED_LOCATIONS_STORAGE_KEY);
  if (!legacy) {
    return;
  }
  localStorage.setItem(SAVED_LOCATIONS_STORAGE_KEY, legacy);
  localStorage.removeItem(LEGACY_SAVED_LOCATIONS_STORAGE_KEY);
}

migrateLegacyGuestLocations();

/** Unified saved-location list: server for auth users, localStorage for guests. */
export function useWeatherLocations(): {
  locations: ComputedRef<Array<WeatherLocation | GuestWeatherLocation>>;
  loading: Ref<boolean>;
  seeding: Ref<boolean>;
  error: Ref<string | null>;
  isAuthenticated: ComputedRef<boolean>;
  isDefaultLocation: (loc: WeatherLocation | GuestWeatherLocation) => boolean;
  addLocation: (label: string, query: string) => Promise<void>;
  removeLocation: (id: number | string) => Promise<void>;
  refresh: () => Promise<void>;
} {
  const auth = useAuthStore();
  const { fetchConfig, isDefaultQuery } = useWeatherConfig();
  const guestLocations = useLocalStorage<GuestWeatherLocation[]>(SAVED_LOCATIONS_STORAGE_KEY, []);
  const serverLocations = ref<WeatherLocation[]>([]);
  const loading = ref(false);
  const seeding = ref(false);
  const error = ref<string | null>(null);
  const defaultSeeded = ref(false);

  const isAuthenticated = computed(() => auth.isAuthenticated);

  const locations = computed(() =>
    isAuthenticated.value ? serverLocations.value : guestLocations.value,
  );

  function isDefaultLocation(loc: WeatherLocation | GuestWeatherLocation): boolean {
    if ("is_default" in loc && loc.is_default) {
      return true;
    }
    return isDefaultQuery(loc.query);
  }

  async function ensureDefaultLocation(): Promise<void> {
    if (defaultSeeded.value || locations.value.length > 0) {
      return;
    }

    seeding.value = true;
    try {
      const { label, query } = await fetchConfig();

      if (isAuthenticated.value) {
        const { data } = await api.post<WeatherLocation>(
          `${TIME_DATE_WEATHER_LOCATION_API_PREFIX}/locations`,
          {
            label,
            query,
          },
        );
        serverLocations.value = [data];
      } else {
        guestLocations.value = [
          {
            id: guestId(),
            label,
            query,
            sort_order: 0,
            is_default: true,
          },
        ];
      }
      defaultSeeded.value = true;
    } catch {
      error.value = "Couldn't initialize default city";
    } finally {
      seeding.value = false;
    }
  }

  async function refresh(): Promise<void> {
    if (!isAuthenticated.value) {
      await ensureDefaultLocation();
      return;
    }
    loading.value = true;
    error.value = null;
    try {
      const { data } = await api.get<WeatherLocation[]>(
        `${TIME_DATE_WEATHER_LOCATION_API_PREFIX}/locations`,
      );
      serverLocations.value = data;
      await ensureDefaultLocation();
    } catch {
      error.value = "Couldn't load saved locations";
    } finally {
      loading.value = false;
    }
  }

  async function addLocation(label: string, query: string): Promise<void> {
    const trimmedQuery = query.trim();
    const trimmedLabel = label.trim() || trimmedQuery;
    if (!trimmedQuery) {
      return;
    }

    if (isAuthenticated.value) {
      const { data } = await api.post<WeatherLocation>(
        `${TIME_DATE_WEATHER_LOCATION_API_PREFIX}/locations`,
        {
          label: trimmedLabel,
          query: trimmedQuery,
        },
      );
      serverLocations.value = [...serverLocations.value, data];
      return;
    }

    const duplicate = guestLocations.value.some(
      (loc) => loc.query.toLowerCase() === trimmedQuery.toLowerCase(),
    );
    if (duplicate) {
      throw new Error("Location already saved");
    }
    if (guestLocations.value.length >= 8) {
      throw new Error("Maximum 8 locations allowed");
    }

    guestLocations.value = [
      ...guestLocations.value,
      {
        id: guestId(),
        label: trimmedLabel,
        query: trimmedQuery,
        sort_order: guestLocations.value.length,
      },
    ];
  }

  async function removeLocation(id: number | string): Promise<void> {
    if (isAuthenticated.value) {
      const target = serverLocations.value.find((loc) => loc.id === id);
      if (target && isDefaultLocation(target)) {
        throw new Error("Default location cannot be removed");
      }
      await api.delete(`${TIME_DATE_WEATHER_LOCATION_API_PREFIX}/locations/${id}`);
      serverLocations.value = serverLocations.value.filter((loc) => loc.id !== id);
      return;
    }

    const target = guestLocations.value.find((loc) => loc.id === id);
    if (target && isDefaultLocation(target)) {
      throw new Error("Default location cannot be removed");
    }

    guestLocations.value = guestLocations.value.filter((loc) => loc.id !== id);
  }

  watch(
    () => auth.isAuthenticated,
    (authenticated) => {
      if (authenticated) {
        void refresh();
      } else {
        void ensureDefaultLocation();
      }
    },
    { immediate: true },
  );

  return {
    locations,
    loading,
    seeding,
    error,
    isAuthenticated,
    isDefaultLocation,
    addLocation,
    removeLocation,
    refresh,
  };
}

/** Merge guest localStorage locations into the server after login. */
export async function syncGuestWeatherLocations(): Promise<void> {
  if (typeof localStorage === "undefined") {
    return;
  }

  let stored: GuestWeatherLocation[] = [];
  try {
    const raw =
      localStorage.getItem(SAVED_LOCATIONS_STORAGE_KEY) ??
      localStorage.getItem(LEGACY_SAVED_LOCATIONS_STORAGE_KEY);
    if (raw) {
      stored = JSON.parse(raw) as GuestWeatherLocation[];
    }
  } catch {
    return;
  }

  if (stored.length === 0) {
    return;
  }

  for (const loc of stored) {
    try {
      await api.post(`${TIME_DATE_WEATHER_LOCATION_API_PREFIX}/locations`, {
        label: loc.label,
        query: loc.query,
      });
    } catch {
      // skip duplicates or limit errors
    }
  }

  localStorage.removeItem(SAVED_LOCATIONS_STORAGE_KEY);
  localStorage.removeItem(LEGACY_SAVED_LOCATIONS_STORAGE_KEY);
}
