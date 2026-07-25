import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import WeatherCityTile from "@/components/weather/WeatherCityTile.vue";

vi.mock("@/components/weather/WeatherSummaryContent.vue", () => ({
  default: {
    name: "WeatherSummaryContent",
    template: "<div data-testid=\"summary\" />",
  },
}));

describe("WeatherCityTile", () => {
  it("emits remove from the close control above the select button", async () => {
    const wrapper = mount(WeatherCityTile, {
      props: { query: "Paris", removable: true },
    });

    const close = wrapper.get('button[aria-label="Remove Paris"]');
    expect(close.classes()).toContain("z-10");

    await close.trigger("click");
    expect(wrapper.emitted("remove")).toHaveLength(1);
    expect(wrapper.emitted("select")).toBeUndefined();
  });
});
