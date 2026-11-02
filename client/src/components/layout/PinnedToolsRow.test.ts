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

vi.mock("@/components/ui/ToastContainer.vue", () => ({
  default: {
    name: "ToastContainer",
    props: ["variant"],
    template: '<div data-testid="toast-host" :data-variant="variant" />',
  },
}));

describe("PinnedToolsRow", () => {
  it("shows toast host without a weather tile in the tool grid", () => {
    mocks.routeName = "calculator";

    const wrapper = mount(PinnedToolsRow);

    expect(wrapper.find(".page-tool-grid").exists()).toBe(true);
    expect(wrapper.find('[data-testid="toast-host"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="toast-host"]').attributes("data-variant")).toBe("tile");
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(false);
    expect(wrapper.find('a[href="/admin/users"]').exists()).toBe(false);
  });

  it("keeps the toast strip on the weather page", () => {
    mocks.routeName = WEATHER_ROUTE_NAME;

    const wrapper = mount(PinnedToolsRow);

    expect(wrapper.find(".page-tool-grid").exists()).toBe(true);
    expect(wrapper.find('[data-testid="toast-host"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(false);
  });

  it("shows the strip on the admin hub", () => {
    mocks.routeName = "admin";

    const wrapper = mount(PinnedToolsRow);

    expect(wrapper.find(".page-tool-grid").exists()).toBe(true);
    expect(wrapper.find('[data-testid="toast-host"]').exists()).toBe(true);
  });

  it("hides the strip on news, settings, and nested admin routes", () => {
    mocks.routeName = "news";
    expect(mount(PinnedToolsRow).find(".page-tool-grid").exists()).toBe(false);

    mocks.routeName = "settings";
    expect(mount(PinnedToolsRow).find(".page-tool-grid").exists()).toBe(false);

    mocks.routeName = "admin-users";
    expect(mount(PinnedToolsRow).find(".page-tool-grid").exists()).toBe(false);
  });
});
