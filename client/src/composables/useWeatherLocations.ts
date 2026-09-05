import { computed, ref, watch, type ComputedRef, type Ref, type WatchStopHandle } from "vue";

import { api } from "@/composables/useApi";
import { useWeatherConfig } from "@/composables/useWeatherConfig";
import {
  LEGACY_SAVED_LOCATIONS_STORAGE_KEY,
  MAX_SAVED_WEATHER_LOCATIONS,
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

/** Shared across all useWeatherLocations() callers (WeatherPage, WeatherBar, …). */
const serverLocations = ref<WeatherLocation[]>([]);
const guestLocations = ref<GuestWeatherLocation[]>(readGuestLocations(SAVED_LOCATIONS_STORAGE_KEY));
const loading = ref(false);
const seeding = ref(false);
const error = ref<string | null>(null);
const defaultSeeded = ref(false);

let refreshPromise: Promise<void> | null = null;
let stopAuthWatch: WatchStopHandle | null = null;
let stopGuestSanitizeWatch: WatchStopHandle | null = null;

function writeGuestStorage(locations: GuestWeatherLocation[]): void {
  if (typeof localStorage === "undefined") {
    return;
  }
  try {
    localStorage.setItem(SAVED_LOCATIONS_STORAGE_KEY, JSON.stringify(locations));
  } catch {
    // ignore quota / private mode
  }
}

function persistGuestLocations(next: GuestWeatherLocation[]): void {
  const sanitized = sanitizeGuestWeatherLocations(next);
  guestLocations.value = sanitized;
  writeGuestStorage(sanitized);
}

/** Reset module cache for tests. */
export function clearWeatherLocations(): void {
  stopAuthWatch?.();
  stopAuthWatch = null;
  stopGuestSanitizeWatch?.();
  stopGuestSanitizeWatch = null;
  serverLocations.value = [];
  guestLocations.value = [];
  loading.value = false;
  seeding.value = false;
  error.value = null;
  defaultSeeded.value = false;
  refreshPromise = null;
  if (typeof localStorage !== "undefined") {
    localStorage.removeItem(SAVED_LOCATIONS_STORAGE_KEY);
  }
}

function ensureGuestSanitizeWatch(): void {
  if (stopGuestSanitizeWatch) {
    return;
  }
  stopGuestSanitizeWatch = watch(
    guestLocations,
    (next) => {
      const sanitized = sanitizeGuestWeatherLocations(next);
      if (JSON.stringify(sanitized) !== JSON.stringify(next)) {
        persistGuestLocations(sanitized);
      }
    },
    { deep: true },
  );
}

function ensureAuthWatch(): void {
  if (stopAuthWatch) {
    return;
  }
  const auth = useAuthStore();
  stopAuthWatch = watch(
    () => auth.isAuthenticated,
    (authenticated) => {
      if (authenticated) {
        void refresh();
      } else {
        // Auth seeding left defaultSeeded true; guests need a fresh seed pass.
        defaultSeeded.value = false;
        serverLocations.value = [];
        void ensureDefaultLocation();
      }
    },
    { immediate: true },
  );
}

async function ensureDefaultLocation(): Promise<void> {
  const auth = useAuthStore();
  const { fetchConfig } = useWeatherConfig();
  const list = auth.isAuthenticated ? serverLocations.value : guestLocations.value;
  if (defaultSeeded.value || list.length > 0) {
    return;
  }

  seeding.value = true;
  try {
    const { query } = await fetchConfig();

    if (auth.isAuthenticated) {
      try {
        const { data } = await api.post<WeatherLocation>(`${WEATHER_API_PREFIX}/locations`, {
          query,
        });
        serverLocations.value = [data];
      } catch {
        error.value = "Couldn't initialize default city";
        return;
      }
    } else {
      persistGuestLocations([
        {
          id: guestId(),
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
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    const auth = useAuthStore();
    if (!auth.isAuthenticated) {
      await ensureDefaultLocation();
      return;
    }
    loading.value = true;
    error.value = null;
    try {
      const { data } = await api.get<WeatherLocation[]>(`${WEATHER_API_PREFIX}/locations`);
      serverLocations.value = data;
    } catch {
      error.value = "Couldn't load saved locations";
    }
    await ensureDefaultLocation();
    loading.value = false;
  })().finally(() => {
    refreshPromise = null;
  });

  return refreshPromise;
}

/** Unified saved-location list: server for auth users, localStorage for guests. */
export function useWeatherLocations(): {
  locations: ComputedRef<Array<WeatherLocation | GuestWeatherLocation>>;
  loading: Ref<boolean>;
  seeding: Ref<boolean>;
  error: Ref<string | null>;
  isAuthenticated: ComputedRef<boolean>;
  isDefaultLocation: (loc: WeatherLocation | GuestWeatherLocation) => boolean;
  addLocation: (query: string) => Promise<void>;
  removeLocation: (id: number | string) => Promise<void>;
  setGuestDefaultByQuery: (query: string) => void;
  refresh: () => Promise<void>;
  maxLocations: ComputedRef<number>;
  canAddLocation: ComputedRef<boolean>;
  guestLimitMessage: ComputedRef<string | null>;
} {
  const auth = useAuthStore();
  const { isDefaultQuery } = useWeatherConfig();

  ensureGuestSanitizeWatch();
  ensureAuthWatch();

  const isAuthenticated = computed(() => auth.isAuthenticated);

  const locations = computed(() =>
    isAuthenticated.value ? serverLocations.value : guestLocations.value,
  );

  const maxLocations = computed(() => MAX_SAVED_WEATHER_LOCATIONS);

  const canAddLocation = computed(() => locations.value.length < maxLocations.value);

  const guestLimitMessage = computed(() =>
    isAuthenticated.value ? null : guestLocationLimitMessage(guestLocations.value.length),
  );

  function isDefaultLocation(loc: WeatherLocation | GuestWeatherLocation): boolean {
    // Guests: once an explicit is_default exists, only that city is locked.
    if (!auth.isAuthenticated) {
      const hasExplicitDefault = guestLocations.value.some((item) => item.is_default === true);
      if (hasExplicitDefault) {
        return "is_default" in loc && loc.is_default === true;
      }
    }
    if ("is_default" in loc && loc.is_default) {
      return true;
    }
    return isDefaultQuery(loc.query);
  }

  function setGuestDefaultByQuery(query: string): void {
    if (auth.isAuthenticated) {
      return;
    }
    const normalized = query.trim().toLowerCase();
    persistGuestLocations(
      guestLocations.value.map((loc) => {
        if (loc.query.toLowerCase() === normalized) {
          return { ...loc, is_default: true };
        }
        const { is_default: _removed, ...rest } = loc;
        return rest;
      }),
    );
  }

  async function addLocation(query: string): Promise<void> {
    const trimmedQuery = query.trim().slice(0, MAX_WEATHER_LOCATION_QUERY_LENGTH);
    if (!trimmedQuery) {
      return;
    }
    if (!isValidWeatherLocationQuery(trimmedQuery)) {
      throw new Error("Location contains invalid characters");
    }

    if (auth.isAuthenticated) {
      try {
        const { data } = await api.post<WeatherLocation>(`${WEATHER_API_PREFIX}/locations`, {
          query: trimmedQuery,
        });
        serverLocations.value = [...serverLocations.value, data];
      } catch {
        throw new Error("Failed to add location");
      }
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
        query: trimmedQuery,
        sort_order: guestLocations.value.length,
      },
    ]);
  }

  async function removeLocation(id: number | string): Promise<void> {
    if (auth.isAuthenticated) {
      const target = serverLocations.value.find((loc) => String(loc.id) === String(id));
      if (target && isDefaultLocation(target)) {
        throw new Error("Default location cannot be removed");
      }
      try {
        await api.delete(`${WEATHER_API_PREFIX}/locations/${id}`);
      } catch {
        throw new Error("Failed to remove location");
      }
      serverLocations.value = serverLocations.value.filter((loc) => String(loc.id) !== String(id));
      return;
    }

    const target = guestLocations.value.find((loc) => String(loc.id) === String(id));
    if (target && isDefaultLocation(target)) {
      throw new Error("Default location cannot be removed");
    }

    persistGuestLocations(guestLocations.value.filter((loc) => String(loc.id) !== String(id)));
  }

  return {
    locations,
    loading,
    seeding,
    error,
    isAuthenticated,
    isDefaultLocation,
    setGuestDefaultByQuery,
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

  await Promise.allSettled(
    stored.map((loc) =>
      api.post(`${WEATHER_API_PREFIX}/locations`, {
        query: loc.query,
      }),
    ),
  );

  localStorage.removeItem(SAVED_LOCATIONS_STORAGE_KEY);
  localStorage.removeItem(LEGACY_SAVED_LOCATIONS_STORAGE_KEY);
  guestLocations.value = [];
}
