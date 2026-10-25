import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ToolsPage from "@/pages/ToolsPage.vue";
import { publicToolsAsServices } from "@/platform/services";
import { groupServicesForToolsPage } from "@/utils/toolsPageGroups";

const useRouteMock = vi.fn(() => ({ query: {} as Record<string, string> }));
const canAccessMock = vi.fn((_slug: string) => false);

vi.mock("vue-router", () => ({
  useRoute: () => useRouteMock(),
  useRouter: () => ({ replace: vi.fn() }),
  RouterLink: {
    name: "RouterLink",
    props: ["to"],
    template: "<a :href=\"typeof to === 'string' ? to : '#'\"><slot /></a>",
  },
}));

vi.mock("@/composables/usePermissions", () => ({
  usePermissions: () => ({
    can: () => false,
    canAccess: (slug: string) => canAccessMock(slug),
  }),
}));

describe("ToolsPage sectioned layout", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    useRouteMock.mockReturnValue({ query: {} });
    canAccessMock.mockReturnValue(false);
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

  it("shows Everyday and Content with demo chips for guests", async () => {
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.findAll('[role="tab"]')).toHaveLength(0);
    expect(wrapper.find('nav[aria-label="tool sections"]').exists()).toBe(false);
    expect(wrapper.text()).toContain("Everyday · 4");
    expect(wrapper.text()).toContain("Content · 2");
    expect(wrapper.text()).toContain("recipes");
    expect(wrapper.text()).toContain("calculator");
    expect(wrapper.text()).toContain("Shorten a long link.");
    expect(wrapper.text()).toContain("Do a quick calculation.");
    expect(wrapper.text()).toContain("demo");
    expect(wrapper.text()).not.toContain("expenses");
    expect(wrapper.text()).not.toContain("productivity");
    expect(wrapper.text()).not.toContain("utilities");
    expect(wrapper.text()).not.toContain("Work");
    expect(wrapper.text()).not.toContain("Builders");
    expect(wrapper.text()).not.toContain("news");
    expect(wrapper.get('[data-testid="crumbs"]').text()).toBe("tools");
  });

  it("shows Work and Builders with yours chips when canAccess allows", async () => {
    canAccessMock.mockImplementation((slug: string) =>
      ["tasks", "file-share", "vid-download", "data-extract"].includes(slug),
    );
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain("Work");
    expect(wrapper.text()).toContain("Builders");
    expect(wrapper.text()).toContain("yours");
    expect(wrapper.find('nav[aria-label="tool sections"]').exists()).toBe(false);
    expect(wrapper.text()).not.toContain("your tools");
  });

  it("shows expenses-off notice when redirected with expenses=off", async () => {
    useRouteMock.mockReturnValue({ query: { expenses: "off" } });
    const wrapper = mountPage();
    await flushPromises();
    expect(wrapper.text()).toContain("Expenses are turned off on this deploy.");
  });
});

describe("tools page group order", () => {
  it("lists Everyday utilities then Content without platform category labels", () => {
    const sections = groupServicesForToolsPage(publicToolsAsServices());
    expect(sections.map((s) => s.label)).toEqual(["Everyday", "Content"]);
    expect(sections[0]?.services.map((tool) => tool.slug)).toEqual([
      "weather",
      "calculator",
      "password-generator",
      "qr-generator",
    ]);
    expect(sections[1]?.services.map((tool) => tool.slug)).toEqual([
      "url-shortener",
      "recipes",
    ]);
  });

  it("excludes health-checker and vid-download from the guest public catalog", () => {
    const slugs = publicToolsAsServices().map((tool) => tool.slug);
    expect(slugs).not.toContain("health-checker");
    expect(slugs).not.toContain("vid-download");
    expect(slugs).not.toContain("expenses");
    expect(slugs).toContain("weather");
  });
});
