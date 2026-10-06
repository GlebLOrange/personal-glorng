import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createMemoryHistory, createRouter } from "vue-router";
import { ref } from "vue";

import NavBar from "@/components/layout/NavBar.vue";

vi.mock("@/composables/useColorTheme", () => ({
  useColorTheme: () => ({
    preference: ref("dark"),
    cyclePreference: vi.fn(),
  }),
}));

vi.mock("@/composables/useScrollDirection", () => ({
  useScrollDirection: () => ({
    isHidden: ref(false),
    show: vi.fn(),
  }),
}));

describe("NavBar", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        addListener: vi.fn(),
        removeListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
    vi.stubGlobal(
      "ResizeObserver",
      class {
        observe(): void {}
        unobserve(): void {}
        disconnect(): void {}
      },
    );
  });

  it("uses SiteLogo on the home link with an accessible name", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: "/", component: { template: "<div />" } }],
    });
    await router.push("/");
    await router.isReady();

    const wrapper = mount(NavBar, {
      global: {
        plugins: [router],
        stubs: {
          NavMobileMenu: true,
          IconActionButton: true,
        },
      },
    });

    const home = wrapper.get('a[aria-label="gleb.y home"]');
    expect(home.classes()).toContain("min-h-11");
    expect(home.classes()).toContain("min-w-11");
    expect(home.find("svg").exists()).toBe(true);
    expect(home.find("svg").attributes("aria-hidden")).toBe("true");
    expect(home.text()).not.toContain("Gleb.Y");
  });
});
