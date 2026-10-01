import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ToolsPage from "@/pages/ToolsPage.vue";
import { groupServicesByCategory, publicToolsAsServices } from "@/platform/services";

const useRouteMock = vi.fn(() => ({ query: {} as Record<string, string> }));

vi.mock("vue-router", () => ({
  useRoute: () => useRouteMock(),
  useRouter: () => ({ replace: vi.fn() }),
  RouterLink: {
    name: "RouterLink",
    props: ["to"],
    template: "<a :href=\"typeof to === 'string' ? to : '#'\"><slot /></a>",
  },
}));

describe("ToolsPage sectioned layout", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    useRouteMock.mockReturnValue({ query: {} });
  });

  function mountPage() {
    return mount(ToolsPage, {
      global: {
        stubs: {
          PageShell: {
            props: ["title", "breadcrumbs", "backTo", "narrow"],
            template:
              '<div><div data-testid="crumbs"><span v-for="(c, i) in breadcrumbs" :key="i">{{ c.label }}</span></div><slot /></div>',
          },
        },
      },
    });
  }

  it("shows all category headings and tiles without tabs", async () => {
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.findAll('[role="tab"]')).toHaveLength(0);
    expect(wrapper.text()).toContain("content");
    expect(wrapper.text()).toContain("utilities");
    expect(wrapper.text()).toContain("recipes");
    expect(wrapper.text()).toContain("calculator");
    expect(wrapper.text()).toMatch(/same FastAPI as the portfolio/i);
    // expenses (only public productivity tool) is off by default via feature flag
    expect(wrapper.text()).not.toContain("expenses");
    expect(wrapper.text()).not.toContain("productivity");
    expect(wrapper.text()).not.toContain("news");
    expect(wrapper.get('[data-testid="crumbs"]').text()).toBe("tools");
  });

  it("shows expenses-off notice when redirected with expenses=off", async () => {
    useRouteMock.mockReturnValue({ query: { expenses: "off" } });
    const wrapper = mountPage();
    await flushPromises();
    expect(wrapper.text()).toContain("Expenses are turned off on this deploy.");
  });
});

describe("tools content tile order", () => {
  it("lists url-shortener before recipes in the content section", () => {
    const content = groupServicesByCategory(publicToolsAsServices()).find(
      (section) => section.category === "content",
    );
    expect(content?.services.map((tool) => tool.slug)).not.toContain("news");
    expect(content?.services.map((tool) => tool.slug)[0]).toBe("url-shortener");
  });

  it("excludes health-checker and vid-download from the guest public catalog", () => {
    const slugs = publicToolsAsServices().map((tool) => tool.slug);
    expect(slugs).not.toContain("health-checker");
    expect(slugs).not.toContain("vid-download");
    expect(slugs).not.toContain("expenses");
    expect(slugs).toContain("weather");
  });
});
