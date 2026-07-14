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
    props: ["wrapperClass", "cardClass"],
    template: '<aside data-testid="weather-bar" />',
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
  });

  it("shows weather without users for guests off the weather page", () => {
    mocks.isSuperuser.value = false;
    mocks.routeName = "calculator";

    const wrapper = mount(PinnedToolsRow);

    expect(wrapper.find('a[href="/admin/users"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(true);
  });

  it("hides the row on the weather page for guests", () => {
    mocks.isSuperuser.value = false;
    mocks.routeName = WEATHER_ROUTE_NAME;

    const wrapper = mount(PinnedToolsRow);

    expect(wrapper.find(".page-tool-grid").exists()).toBe(false);
  });

  it("hides users tile on the weather page for superusers", () => {
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

    expect(wrapper.find(".page-tool-grid").exists()).toBe(true);
    expect(wrapper.find('a[href="/admin/users"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="weather-bar"]').exists()).toBe(true);
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
