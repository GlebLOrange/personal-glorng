import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ToolsPage from "@/pages/ToolsPage.vue";
import { groupServicesByCategory, publicToolsAsServices } from "@/platform/services";

const mocks = vi.hoisted(() => ({
  replace: vi.fn(),
  routeQuery: {} as Record<string, unknown>,
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ query: mocks.routeQuery }),
  useRouter: () => ({ replace: mocks.replace }),
  RouterLink: {
    name: "RouterLink",
    props: ["to"],
    template: '<a :href="typeof to === \'string\' ? to : \'#\'"><slot /></a>',
  },
}));

describe("ToolsPage category tabs", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    mocks.routeQuery = {};
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

  it("defaults to content and writes ?category=content", async () => {
    mountPage();
    await flushPromises();

    expect(mocks.replace).toHaveBeenCalledWith({
      query: { category: "content" },
    });
  });

  it("keeps a valid category query without rewriting", async () => {
    mocks.routeQuery = { category: "utilities" };
    const wrapper = mountPage();
    await flushPromises();

    expect(mocks.replace).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain("calculator");
    expect(wrapper.text()).not.toContain("news");
  });

  it("shows category breadcrumb and hides empty-category tabs", async () => {
    mocks.routeQuery = { category: "content" };
    const wrapper = mountPage();
    await flushPromises();

    const crumbText = wrapper.get('[data-testid="crumbs"]').text();
    expect(crumbText).toContain("tools");
    expect(crumbText).toContain("content");

    const tabLabels = wrapper.findAll('[role="tab"]').map((tab) => tab.text());
    // expenses (only public productivity tool) is off by default via feature flag
    expect(tabLabels).toEqual(["content", "utilities"]);
    expect(tabLabels).not.toContain("operations");
    expect(tabLabels).not.toContain("productivity");
    expect(wrapper.text()).not.toContain("expenses");
  });

  it("switches category via tab and updates the query", async () => {
    mocks.routeQuery = { category: "content" };
    const wrapper = mountPage();
    await flushPromises();

    const utilitiesTab = wrapper.findAll('[role="tab"]').find((tab) => tab.text() === "utilities");
    expect(utilitiesTab).toBeTruthy();
    await utilitiesTab!.trigger("click");

    expect(mocks.replace).toHaveBeenCalledWith({
      query: { category: "utilities" },
    });
  });
});

describe("tools content tile order", () => {
  it("lists news before other content tools", () => {
    const content = groupServicesByCategory(publicToolsAsServices()).find(
      (section) => section.category === "content",
    );
    expect(content?.services.map((tool) => tool.slug)[0]).toBe("news");
  });
});
