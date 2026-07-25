import { createPinia, setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/composables/useApi";
import {
  clearWeatherLocations,
  useWeatherLocations,
} from "@/composables/useWeatherLocations";
import { useAuthStore } from "@/stores/auth";
import type { UserResponse, WeatherLocation } from "@/types";

vi.mock("@/composables/useApi", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock("@/composables/useWeatherConfig", () => ({
  useWeatherConfig: () => ({
    config: { value: { query: "Wroclaw" } },
    loaded: { value: true },
    fetchConfig: vi.fn(async () => ({ query: "Wroclaw" })),
    isDefaultQuery: (query: string) => query.trim().toLowerCase() === "wroclaw",
  }),
}));

function makeUser(): UserResponse {
  return {
    id: "1",
    email: "a@b.c",
    permissions: [],
    is_verified: true,
    display_name: "User",
    timezone: "UTC",
    preferences: {},
    created_at: "2026-01-01T00:00:00Z",
  };
}

describe("useWeatherLocations", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    clearWeatherLocations();
    vi.mocked(api.get).mockReset();
    vi.mocked(api.post).mockReset();
    vi.mocked(api.delete).mockReset();
  });

  afterEach(() => {
    clearWeatherLocations();
  });

  it("shares the same location list across callers", async () => {
    const first = useWeatherLocations();
    const second = useWeatherLocations();

    // Guest auth watch seeds default city.
    await vi.waitFor(() => expect(first.locations.value.length).toBe(1));

    expect(second.locations.value).toEqual(first.locations.value);
    expect(first.locations.value[0]?.query).toBe("Wroclaw");
  });

  it("guest removeLocation drops the city for every caller", async () => {
    const first = useWeatherLocations();
    const second = useWeatherLocations();

    await vi.waitFor(() => expect(first.locations.value.length).toBe(1));

    await first.addLocation("Paris");
    expect(first.locations.value).toHaveLength(2);
    expect(second.locations.value).toHaveLength(2);

    const paris = first.locations.value.find((loc) => loc.query === "Paris");
    expect(paris).toBeDefined();

    await first.removeLocation(paris!.id);

    expect(first.locations.value.map((loc) => loc.query)).toEqual(["Wroclaw"]);
    expect(second.locations.value.map((loc) => loc.query)).toEqual(["Wroclaw"]);
  });

  it("auth removeLocation filters shared serverLocations after delete", async () => {
    const auth = useAuthStore();
    const locations: WeatherLocation[] = [
      { id: 1, query: "Wroclaw", sort_order: 0 },
      { id: 2, query: "Paris", sort_order: 1 },
    ];
    vi.mocked(api.get).mockResolvedValue({ data: locations });
    vi.mocked(api.delete).mockResolvedValue({ data: undefined });

    auth.user = makeUser();

    const first = useWeatherLocations();
    const second = useWeatherLocations();

    await vi.waitFor(() => expect(first.locations.value).toHaveLength(2));

    await first.removeLocation(2);

    expect(api.delete).toHaveBeenCalledWith("/weather/locations/2");
    expect(first.locations.value.map((loc) => loc.query)).toEqual(["Wroclaw"]);
    expect(second.locations.value.map((loc) => loc.query)).toEqual(["Wroclaw"]);
  });

  it("guest with explicit default only locks that city", async () => {
    const { addLocation, setGuestDefaultByQuery, isDefaultLocation, locations } =
      useWeatherLocations();

    await vi.waitFor(() => expect(locations.value.length).toBe(1));
    await addLocation("Paris");
    setGuestDefaultByQuery("Paris");

    const wroclaw = locations.value.find((loc) => loc.query === "Wroclaw")!;
    const paris = locations.value.find((loc) => loc.query === "Paris")!;

    expect(isDefaultLocation(paris)).toBe(true);
    expect(isDefaultLocation(wroclaw)).toBe(false);
  });
});
