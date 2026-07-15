import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import WeatherPinnedCitiesRow from "@/components/weather/WeatherPinnedCitiesRow.vue";

vi.mock("@/components/weather/WeatherBar.vue", () => ({
  default: {
    name: "WeatherBar",
    props: ["wrapperClass", "cardClass", "expanded"],
    template:
      '<aside data-testid="weather-bar" :data-wrapper-class="wrapperClass" :data-expanded="expanded" />',
  },
}));

vi.mock("@/components/weather/WeatherCityTile.vue", () => ({
  default: {
    name: "WeatherCityTile",
    props: ["label", "query", "removable"],
    emits: ["select", "remove"],
    template: `<div data-testid="weather-city-tile" :data-label="label" :data-removable="removable">
      <button data-testid="select-city" @click="$emit('select')">{{ label }}</button>
      <button v-if="removable" data-testid="remove-city" @click="$emit('remove')">Remove</button>
    </div>`,
  },
}));

const locations = [
  { id: "1", label: "London", query: "London" },
  { id: "2", label: "Paris", query: "Paris" },
  { id: "3", label: "Wrocław", query: "Wroclaw", is_default: true },
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
  it("shows active city in column 3 and up to two other cities", () => {
    const wrapper = mountRow();

    expect(wrapper.find('[data-testid="weather-bar"]').attributes("data-wrapper-class")).toBe(
      "page-tile md:col-start-3",
    );
    expect(wrapper.find('[data-testid="weather-bar"]').attributes("data-expanded")).not.toBe(
      "false",
    );

    const cityTiles = wrapper.findAll('[data-testid="weather-city-tile"]');
    expect(cityTiles).toHaveLength(2);
    expect(cityTiles[0]?.attributes("data-label")).toBe("London");
    expect(cityTiles[1]?.attributes("data-label")).toBe("Paris");
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

    expect(wrapper.find('[aria-label="Loading cities"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(false);
  });

  it("shows empty state when there are no cities", () => {
    const wrapper = mountRow({ locations: [] });

    expect(wrapper.text()).toContain("No cities yet");
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(false);
  });
});
