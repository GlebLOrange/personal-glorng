import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import PinnedToolsRow from "@/components/layout/PinnedToolsRow.vue";
import { WEATHER_ROUTE_NAME } from "@/constants/weather";

const mocks = vi.hoisted(() => ({
  routeName: "calculator" as string | symbol | null | undefined,
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ name: mocks.routeName }),
}));

vi.mock("@/components/weather/WeatherBar.vue", () => ({
  default: {
    name: "WeatherBar",
    props: ["wrapperClass", "cardClass", "expanded"],
    template:
      '<aside data-testid="weather-bar" :data-wrapper-class="wrapperClass" :data-expanded="expanded" />',
  },
}));

vi.mock("@/components/ui/ToastContainer.vue", () => ({
  default: {
    name: "ToastContainer",
    template: '<div data-testid="toast-host" />',
  },
}));

describe("PinnedToolsRow", () => {
  it("shows toast host and weather tile in the tool grid", () => {
    mocks.routeName = "calculator";

    const wrapper = mount(PinnedToolsRow);

    expect(wrapper.find(".page-tool-grid").exists()).toBe(true);
    expect(wrapper.find('[data-testid="toast-host"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="weather-bar"]').attributes("data-wrapper-class")).toBe(
      "page-tile md:col-start-3",
    );
    expect(wrapper.find('a[href="/admin/users"]').exists()).toBe(false);
  });

  it("keeps the grid on the weather page", () => {
    mocks.routeName = WEATHER_ROUTE_NAME;

    const wrapper = mount(PinnedToolsRow);

    expect(wrapper.find(".page-tool-grid").exists()).toBe(true);
    expect(wrapper.find('[data-testid="toast-host"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(true);
  });
});
