import { onMounted, ref, type Ref } from "vue";

export type GeolocationStatus = "pending" | "granted" | "denied" | "unsupported";

export interface GeolocationCoords {
  lat: number;
  lon: number;
}

/** Browser geolocation with permission state tracking. */
export function useGeolocation(): {
  status: Ref<GeolocationStatus>;
  coords: Ref<GeolocationCoords | null>;
  error: Ref<string | null>;
  request: () => void;
} {
  const status = ref<GeolocationStatus>("pending");
  const coords = ref<GeolocationCoords | null>(null);
  const error = ref<string | null>(null);

  function request(): void {
    if (!navigator.geolocation) {
      status.value = "unsupported";
      error.value = "Geolocation is not supported in this browser";
      return;
    }

    status.value = "pending";
    error.value = null;

    navigator.geolocation.getCurrentPosition(
      (position) => {
        status.value = "granted";
        coords.value = {
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        };
      },
      (err) => {
        status.value = "denied";
        error.value = err.message || "Location access denied";
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
    );
  }

  onMounted(request);

  return { status, coords, error, request };
}

/** Format coordinates for weather API lookup. */
export function coordsQuery(lat: number, lon: number): string {
  return `${lat.toFixed(4)},${lon.toFixed(4)}`;
}
