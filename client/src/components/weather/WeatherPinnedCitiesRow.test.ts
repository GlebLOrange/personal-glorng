import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import WeatherPinnedCitiesRow from "@/components/weather/WeatherPinnedCitiesRow.vue";

vi.mock("@/components/weather/WeatherCityTile.vue", () => ({
  default: {
    name: "WeatherCityTile",
    props: ["query", "removable"],
    emits: ["select", "remove"],
    template: `<div data-testid="weather-city-tile" :data-query="query" :data-removable="removable">
      <button data-testid="select-city" @click="$emit('select')">{{ query }}</button>
      <button v-if="removable" data-testid="remove-city" @click="$emit('remove')">Remove</button>
    </div>`,
  },
}));

const locations = [
  { id: "1", query: "London" },
  { id: "2", query: "Paris" },
  { id: "3", query: "Wroclaw", is_default: true },
];

function mountRow(overrides: Record<string, unknown> = {}) {
  return mount(WeatherPinnedCitiesRow, {
    props: {
      locations,
      activeQuery: "Wroclaw",
      loading: false,
      seeding: false,
      isDefaultLocation: (loc: { query: string; is_default?: boolean }) =>
        Boolean(loc.is_default) || loc.query === "Wroclaw",
      ...overrides,
    },
  });
}

describe("WeatherPinnedCitiesRow", () => {
  it("shows other cities without embedding the active weather bar", () => {
    const wrapper = mountRow();

    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(false);

    const cityTiles = wrapper.findAll('[data-testid="weather-city-tile"]');
    expect(cityTiles).toHaveLength(2);
    expect(cityTiles[0]?.attributes("data-query")).toBe("London");
    expect(cityTiles[1]?.attributes("data-query")).toBe("Paris");
  });

  it("emits select when a city tile is clicked", async () => {
    const wrapper = mountRow();

    await wrapper.findAll('[data-testid="select-city"]')[0]?.trigger("click");

    expect(wrapper.emitted("select")?.[0]).toEqual(["London"]);
  });

  it("emits remove for removable city tiles", async () => {
    const wrapper = mountRow();

    await wrapper.findAll('[data-testid="remove-city"]')[0]?.trigger("click");

    expect(wrapper.emitted("remove")?.[0]).toEqual(["1"]);
  });

  it("shows loading skeletons while busy", () => {
    const wrapper = mountRow({ loading: true });

    expect(wrapper.find('[aria-label="loading cities"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="weather-city-tile"]').exists()).toBe(false);
  });

  it("shows empty state when there are no cities", () => {
    const wrapper = mountRow({ locations: [] });

    expect(wrapper.text()).toContain("No cities yet");
    expect(wrapper.find('[data-testid="weather-city-tile"]').exists()).toBe(false);
  });
});
