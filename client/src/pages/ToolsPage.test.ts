import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { computed, ref } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ToolsPage from "@/pages/ToolsPage.vue";
import { publicToolsAsServices } from "@/platform/services";
import { groupServicesForToolsPage } from "@/utils/toolsPageGroups";

const useRouteMock = vi.fn(() => ({ query: {} as Record<string, string> }));
const canAccessMock = vi.fn((_slug: string) => false);
const isSuperuserRef = ref(false);

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
    isSuperuser: computed(() => isSuperuserRef.value),
  }),
}));

vi.mock("@/utils/featureFlags", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/utils/featureFlags")>();
  return {
    ...actual,
    isAiChatEnabled: vi.fn(() => true),
  };
});

import { isAiChatEnabled } from "@/utils/featureFlags";

describe("ToolsPage sectioned layout", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    useRouteMock.mockReturnValue({ query: {} });
    canAccessMock.mockReturnValue(false);
    isSuperuserRef.value = false;
    vi.mocked(isAiChatEnabled).mockReturnValue(true);
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
    expect(wrapper.text()).toContain("Everyday");
    expect(wrapper.text()).toContain("Content");
    expect(wrapper.text()).toContain("4 tools");
    expect(wrapper.text()).toContain("2 tools");
    expect(wrapper.text()).toContain("recipes");
    expect(wrapper.text()).toContain("calculator");
    expect(wrapper.text()).toContain("short links");
    expect(wrapper.text()).toContain("quick math");
    expect(wrapper.text()).toContain("demo");
    expect(wrapper.text()).not.toContain("expenses");
    expect(wrapper.text()).not.toContain("productivity");
    expect(wrapper.text()).not.toContain("utilities");
    expect(wrapper.text()).not.toContain("Work");
    expect(wrapper.text()).not.toContain("Builders");
    expect(wrapper.text()).not.toContain("news");
    expect(wrapper.findAll("h2").some((h) => h.text() === "admin")).toBe(false);
    expect(wrapper.text()).not.toContain("audit logs");
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
    expect(wrapper.text()).toContain("tasks and reminders");
    expect(wrapper.text()).toContain("share files");
    expect(wrapper.text()).toContain("save videos");
    expect(wrapper.text()).toContain("rows from files");
    expect(wrapper.find('nav[aria-label="tool sections"]').exists()).toBe(false);
    expect(wrapper.text()).not.toContain("your tools");
  });

  it("shows expenses-off notice when redirected with expenses=off", async () => {
    useRouteMock.mockReturnValue({ query: { expenses: "off" } });
    const wrapper = mountPage();
    await flushPromises();
    expect(wrapper.text()).toContain("Expenses are turned off on this deploy.");
  });

  it("shows access-denied notice when redirected with access=denied", async () => {
    useRouteMock.mockReturnValue({ query: { access: "denied" } });
    const wrapper = mountPage();
    await flushPromises();
    expect(wrapper.text()).toContain("You do not have access to that admin tool");
  });

  it("hides admin hub tiles from capability-only users", async () => {
    canAccessMock.mockImplementation((slug: string) => slug === "feedback");
    isSuperuserRef.value = false;

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.findAll("h2").some((h) => h.text() === "admin")).toBe(false);
    expect(wrapper.text()).not.toContain("audit logs");
  });

  function tileTitleCount(wrapper: ReturnType<typeof mountPage>, name: string): number {
    return wrapper.findAll("h3, h4").filter((heading) => heading.text().trim() === name).length;
  }

  it("shows admin hub tiles for superusers without duplicating catalog tools", async () => {
    isSuperuserRef.value = true;

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.findAll("h2").some((h) => h.text() === "admin")).toBe(false);
    expect(wrapper.text()).toContain("audit logs");
    expect(wrapper.text()).toContain("ai chat");
    expect(tileTitleCount(wrapper, "weather")).toBe(1);
    expect(tileTitleCount(wrapper, "url shortener")).toBe(1);
    expect(tileTitleCount(wrapper, "recipes")).toBe(1);
    expect(tileTitleCount(wrapper, "tasks")).toBe(1);
  });

  it("keeps tasks once when the catalog already lists them", async () => {
    canAccessMock.mockImplementation((slug: string) => slug === "tasks");
    isSuperuserRef.value = true;

    const wrapper = mountPage();
    await flushPromises();

    expect(tileTitleCount(wrapper, "tasks")).toBe(1);
    expect(wrapper.text()).toContain("audit logs");
  });

  it("omits ai chat from admin tiles when the feature flag is off", async () => {
    vi.mocked(isAiChatEnabled).mockReturnValue(false);
    isSuperuserRef.value = true;

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.findAll("h2").some((h) => h.text() === "admin")).toBe(false);
    expect(wrapper.text()).toContain("audit logs");
    expect(wrapper.text()).not.toContain("ai chat");
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
