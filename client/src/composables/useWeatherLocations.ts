import { computed, ref, watch, type ComputedRef, type Ref } from "vue";

import { api } from "@/composables/useApi";
import { useLocalStorage } from "@/composables/useLocalStorage";
import { useAuthStore } from "@/stores/auth";
import type { WeatherLocation } from "@/types";

const STORAGE_KEY = "weather:saved-locations";

export interface GuestWeatherLocation {
  id: string;
  label: string;
  query: string;
  sort_order: number;
}

function guestId(): string {
  return crypto.randomUUID();
}

/** Unified saved-location list: server for auth users, localStorage for guests. */
export function useWeatherLocations(): {
  locations: ComputedRef<Array<WeatherLocation | GuestWeatherLocation>>;
  loading: Ref<boolean>;
  error: Ref<string | null>;
  isAuthenticated: ComputedRef<boolean>;
  addLocation: (label: string, query: string) => Promise<void>;
  removeLocation: (id: number | string) => Promise<void>;
  refresh: () => Promise<void>;
} {
  const auth = useAuthStore();
  const guestLocations = useLocalStorage<GuestWeatherLocation[]>(STORAGE_KEY, []);
  const serverLocations = ref<WeatherLocation[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => auth.isAuthenticated);

  const locations = computed(() =>
    isAuthenticated.value ? serverLocations.value : guestLocations.value,
  );

  async function refresh(): Promise<void> {
    if (!isAuthenticated.value) {
      return;
    }
    loading.value = true;
    error.value = null;
    try {
      const { data } = await api.get<WeatherLocation[]>("/weather/locations");
      serverLocations.value = data;
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
      const { data } = await api.post<WeatherLocation>("/weather/locations", {
        label: trimmedLabel,
        query: trimmedQuery,
      });
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
      await api.delete(`/weather/locations/${id}`);
      serverLocations.value = serverLocations.value.filter((loc) => loc.id !== id);
      return;
    }

    guestLocations.value = guestLocations.value.filter((loc) => loc.id !== id);
  }

  watch(
    () => auth.isAuthenticated,
    (authenticated) => {
      if (authenticated) {
        void refresh();
      }
    },
    { immediate: true },
  );

  return {
    locations,
    loading,
    error,
    isAuthenticated,
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
    const raw = localStorage.getItem(STORAGE_KEY);
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
      await api.post("/weather/locations", {
        label: loc.label,
        query: loc.query,
      });
    } catch {
      // skip duplicates or limit errors
    }
  }

  localStorage.removeItem(STORAGE_KEY);
}
