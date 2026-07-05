import { computed, ref, watch, type ComputedRef, type Ref } from "vue";

import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useLocalStorage } from "@/composables/useLocalStorage";
import { useWeatherConfig } from "@/composables/useWeatherConfig";
import {
  LEGACY_SAVED_LOCATIONS_STORAGE_KEY,
  MAX_SAVED_WEATHER_LOCATIONS,
  MAX_WEATHER_LOCATION_LABEL_LENGTH,
  MAX_WEATHER_LOCATION_QUERY_LENGTH,
  SAVED_LOCATIONS_STORAGE_KEY,
  WEATHER_API_PREFIX,
} from "@/constants/weather";
import { useAuthStore } from "@/stores/auth";
import type { WeatherLocation } from "@/types";
import {
  guestLocationLimitMessage,
  sanitizeGuestWeatherLocations,
  type GuestWeatherLocation,
} from "@/utils/guestWeatherLocations";
import { isValidWeatherLocationQuery } from "@/utils/weather";

export type { GuestWeatherLocation };

function readGuestLocations(key: string): GuestWeatherLocation[] {
  if (typeof localStorage === "undefined") {
    return [];
  }
  try {
    const raw = localStorage.getItem(key);
    if (raw === null) {
      return [];
    }
    return sanitizeGuestWeatherLocations(JSON.parse(raw));
  } catch {
    return [];
  }
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
  maxLocations: ComputedRef<number>;
  canAddLocation: ComputedRef<boolean>;
  guestLimitMessage: ComputedRef<string | null>;
} {
  const auth = useAuthStore();
  const { fetchConfig, isDefaultQuery } = useWeatherConfig();
  const guestLocations = useLocalStorage<GuestWeatherLocation[]>(SAVED_LOCATIONS_STORAGE_KEY, []);
  const { run: runList } = useApiAction({ silent: true, logContext: "weather-locations" });
  const { run: runMutate } = useApiAction({ silent: true, logContext: "weather-locations" });

  if (typeof localStorage !== "undefined") {
    const sanitized = readGuestLocations(SAVED_LOCATIONS_STORAGE_KEY);
    if (
      localStorage.getItem(SAVED_LOCATIONS_STORAGE_KEY) !== null &&
      JSON.stringify(sanitized) !== JSON.stringify(guestLocations.value)
    ) {
      guestLocations.value = sanitized;
    }
  }
  const serverLocations = ref<WeatherLocation[]>([]);
  const loading = ref(false);
  const seeding = ref(false);
  const error = ref<string | null>(null);
  const defaultSeeded = ref(false);

  const isAuthenticated = computed(() => auth.isAuthenticated);

  const locations = computed(() =>
    isAuthenticated.value ? serverLocations.value : guestLocations.value,
  );

  const maxLocations = computed(() => MAX_SAVED_WEATHER_LOCATIONS);

  const canAddLocation = computed(() => locations.value.length < maxLocations.value);

  const guestLimitMessage = computed(() =>
    isAuthenticated.value ? null : guestLocationLimitMessage(guestLocations.value.length),
  );

  function persistGuestLocations(next: GuestWeatherLocation[]): void {
    guestLocations.value = sanitizeGuestWeatherLocations(next);
  }

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
        const result = await runMutate(
          () =>
            api.post<WeatherLocation>(`${WEATHER_API_PREFIX}/locations`, {
              label,
              query,
            }),
          { errorFallback: "Couldn't initialize default city" },
        );
        if (result) {
          serverLocations.value = [result.data];
        }
      } else {
        persistGuestLocations([
          {
            id: guestId(),
            label,
            query,
            sort_order: 0,
            is_default: true,
          },
        ]);
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
    const result = await runList(
      () => api.get<WeatherLocation[]>(`${WEATHER_API_PREFIX}/locations`),
      { errorFallback: "Couldn't load saved locations" },
    );
    if (result) {
      serverLocations.value = result.data;
    } else {
      error.value = "Couldn't load saved locations";
    }
    await ensureDefaultLocation();
    loading.value = false;
  }

  async function addLocation(label: string, query: string): Promise<void> {
    const trimmedQuery = query.trim().slice(0, MAX_WEATHER_LOCATION_QUERY_LENGTH);
    const trimmedLabel = (label.trim() || trimmedQuery).slice(0, MAX_WEATHER_LOCATION_LABEL_LENGTH);
    if (!trimmedQuery) {
      return;
    }
    if (!isValidWeatherLocationQuery(trimmedQuery)) {
      throw new Error("Location contains invalid characters");
    }

    if (isAuthenticated.value) {
      const result = await runMutate(
        () =>
          api.post<WeatherLocation>(`${WEATHER_API_PREFIX}/locations`, {
            label: trimmedLabel,
            query: trimmedQuery,
          }),
        { silent: true },
      );
      if (!result) {
        throw new Error("Failed to add location");
      }
      serverLocations.value = [...serverLocations.value, result.data];
      return;
    }

    const duplicate = guestLocations.value.some(
      (loc) => loc.query.toLowerCase() === trimmedQuery.toLowerCase(),
    );
    if (duplicate) {
      throw new Error("Location already saved");
    }
    if (guestLocations.value.length >= MAX_SAVED_WEATHER_LOCATIONS) {
      throw new Error(`Maximum ${MAX_SAVED_WEATHER_LOCATIONS} locations allowed`);
    }

    persistGuestLocations([
      ...guestLocations.value,
      {
        id: guestId(),
        label: trimmedLabel,
        query: trimmedQuery,
        sort_order: guestLocations.value.length,
      },
    ]);
  }

  async function removeLocation(id: number | string): Promise<void> {
    if (isAuthenticated.value) {
      const target = serverLocations.value.find((loc) => loc.id === id);
      if (target && isDefaultLocation(target)) {
        throw new Error("Default location cannot be removed");
      }
      const result = await runMutate(
        () => api.delete(`${WEATHER_API_PREFIX}/locations/${id}`),
        { silent: true },
      );
      if (result === undefined) {
        throw new Error("Failed to remove location");
      }
      serverLocations.value = serverLocations.value.filter((loc) => loc.id !== id);
      return;
    }

    const target = guestLocations.value.find((loc) => loc.id === id);
    if (target && isDefaultLocation(target)) {
      throw new Error("Default location cannot be removed");
    }

    persistGuestLocations(guestLocations.value.filter((loc) => loc.id !== id));
  }

  watch(
    guestLocations,
    (next) => {
      if (isAuthenticated.value) {
        return;
      }
      const sanitized = sanitizeGuestWeatherLocations(next);
      if (JSON.stringify(sanitized) !== JSON.stringify(next)) {
        guestLocations.value = sanitized;
      }
    },
    { deep: true },
  );

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
    maxLocations,
    canAddLocation,
    guestLimitMessage,
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
      stored = sanitizeGuestWeatherLocations(JSON.parse(raw));
    }
  } catch {
    return;
  }

  if (stored.length === 0) {
    return;
  }

  for (const loc of stored) {
    try {
      await api.post(`${WEATHER_API_PREFIX}/locations`, {
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
