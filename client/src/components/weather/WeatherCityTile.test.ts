import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import WeatherCityTile from "@/components/weather/WeatherCityTile.vue";

vi.mock("@/components/weather/WeatherSummaryContent.vue", () => ({
  default: {
    name: "WeatherSummaryContent",
    props: ["query", "interactive"],
    template:
      '<div data-testid="summary" :data-interactive="interactive" :data-query="query" />',
  },
}));

describe("WeatherCityTile", () => {
  it("emits remove from the close control above the select button", async () => {
    const wrapper = mount(WeatherCityTile, {
      props: { query: "Paris", removable: true },
    });

    const close = wrapper.get('button[aria-label="remove Paris"]');
    expect(close.classes()).toContain("z-10");

    await close.trigger("click");
    expect(wrapper.emitted("remove")).toHaveLength(1);
    expect(wrapper.emitted("select")).toBeUndefined();
  });

  it("marks the active city with selected chrome and a non-interactive summary", () => {
    const wrapper = mount(WeatherCityTile, {
      props: { query: "Wroclaw", active: true },
    });

    const select = wrapper.get('button[aria-label="Wroclaw (active city)"]');
    expect(select.attributes("aria-current")).toBe("true");
    expect(select.attributes("aria-selected")).toBe("true");
    expect(wrapper.get(".page-weather-tile-card").classes()).toContain("border-accent-blue");
    expect(wrapper.get('[data-testid="summary"]').attributes("data-interactive")).toBe("false");
  });
});
