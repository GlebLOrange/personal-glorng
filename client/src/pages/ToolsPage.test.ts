import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ToolsPage from "@/pages/ToolsPage.vue";
import { groupServicesByCategory, publicToolsAsServices } from "@/platform/services";

vi.mock("vue-router", () => ({
  useRoute: () => ({ query: {} }),
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
    // expenses (only public productivity tool) is off by default via feature flag
    expect(wrapper.text()).not.toContain("expenses");
    expect(wrapper.text()).not.toContain("productivity");
    expect(wrapper.text()).not.toContain("news");
    expect(wrapper.get('[data-testid="crumbs"]').text()).toBe("tools");
  });
});

describe("tools content tile order", () => {
  it("lists recipes before other content tools when news is not public", () => {
    const content = groupServicesByCategory(publicToolsAsServices()).find(
      (section) => section.category === "content",
    );
    expect(content?.services.map((tool) => tool.slug)).not.toContain("news");
    expect(content?.services.map((tool) => tool.slug)[0]).toBe("recipes");
  });
});
