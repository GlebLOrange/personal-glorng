import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import PinnedToolsRow from "@/components/layout/PinnedToolsRow.vue";
import { WEATHER_ROUTE_NAME } from "@/constants/weather";

const mocks = vi.hoisted(() => ({
  isSuperuser: { value: false },
  routeName: "calculator" as string | symbol | null | undefined,
}));

vi.mock("@/composables/usePermissions", () => ({
  usePermissions: () => ({ isSuperuser: mocks.isSuperuser }),
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

describe("PinnedToolsRow", () => {
  it("shows the users tile for superusers", () => {
    mocks.isSuperuser.value = true;
    mocks.routeName = "admin";

    const wrapper = mount(PinnedToolsRow, {
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a :href="to"><slot /></a>',
          },
        },
      },
    });

    expect(wrapper.get('a[href="/admin/users"]').text()).toContain("users");
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="weather-bar"]').attributes("data-wrapper-class")).toBe(
      "page-tile md:col-start-3",
    );
  });

  it("shows weather without users for guests off the weather page", () => {
    mocks.isSuperuser.value = false;
    mocks.routeName = "calculator";

    const wrapper = mount(PinnedToolsRow);

    expect(wrapper.find('a[href="/admin/users"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="weather-bar"]').attributes("data-expanded")).toBeUndefined();
  });

  it("hides the pinned row on the weather page", () => {
    mocks.isSuperuser.value = false;
    mocks.routeName = WEATHER_ROUTE_NAME;

    const wrapper = mount(PinnedToolsRow);

    expect(wrapper.find(".page-tool-grid").exists()).toBe(false);
  });

  it("hides the pinned row for superusers on weather page", () => {
    mocks.isSuperuser.value = true;
    mocks.routeName = WEATHER_ROUTE_NAME;

    const wrapper = mount(PinnedToolsRow, {
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a :href="to"><slot /></a>',
          },
        },
      },
    });

    expect(wrapper.find(".page-tool-grid").exists()).toBe(false);
  });

  it("hides users tile for superusers off the admin dashboard", () => {
    mocks.isSuperuser.value = true;
    mocks.routeName = "calculator";

    const wrapper = mount(PinnedToolsRow, {
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a :href="to"><slot /></a>',
          },
        },
      },
    });

    expect(wrapper.find('a[href="/admin/users"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(true);
  });
});
