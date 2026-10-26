import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { computed, ref } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ToolsPage from "@/pages/ToolsPage.vue";
import { publicToolsAsServices } from "@/platform/services";
import { useAuthStore } from "@/stores/auth";
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
    template: '<a :href="typeof to === \'string\' ? to : \'#\'"><slot /></a>',
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

describe("ToolsPage spoiler catalog", () => {
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

  it("opens utils and content spoilers; utils is tab pills only for guests", async () => {
    const wrapper = mountPage();
    await flushPromises();

    const spoilers = wrapper.findAll("details");
    expect(spoilers.length).toBeGreaterThanOrEqual(2);
    expect(spoilers.every((el) => el.attributes("open") !== undefined)).toBe(true);

    const utils = wrapper.get("#utils");
    expect(utils.find('[aria-label="utils tools"]').exists()).toBe(true);
    expect(utils.text()).toContain("weather");
    expect(utils.text()).toContain("calculator");
    expect(utils.text()).toContain("password generator");
    expect(utils.text()).toContain("qr generator");
    expect(utils.text()).not.toContain("video downloader");
    expect(utils.text()).not.toContain("send email");
    expect(utils.text()).not.toContain("quick math");
    expect(utils.text()).not.toContain("demo");
    expect(utils.findAll("h3, h4")).toHaveLength(0);

    expect(wrapper.text()).toContain("content");
    expect(wrapper.text()).toContain("recipes");
    expect(wrapper.text()).toContain("short links");
    expect(wrapper.text()).toContain("demo");
    expect(wrapper.text()).not.toContain("server");
    expect(wrapper.text()).not.toContain("expenses");
    expect(wrapper.text()).not.toContain("Everyday");
    expect(wrapper.get('[data-testid="crumbs"]').text()).toBe("tools");
  });

  it("shows Video pill when authenticated with access", async () => {
    const auth = useAuthStore();
    auth.sessionResolved = true;
    auth.user = {
      id: 1,
      email: "op@example.com",
      display_name: "op",
      is_active: true,
      permissions: ["vid-download:read"],
    } as never;
    canAccessMock.mockImplementation((slug: string) => slug === "vid-download");

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.get("#utils").text()).toContain("video downloader");
    expect(wrapper.get("#utils").text()).not.toContain("save videos");
  });

  it("shows yours chips on content tiles when canAccess allows extras", async () => {
    canAccessMock.mockImplementation((slug: string) =>
      ["tasks", "file-share", "data-extract"].includes(slug),
    );
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain("yours");
    expect(wrapper.text()).toContain("tasks and reminders");
    expect(wrapper.text()).toContain("share files");
    expect(wrapper.text()).toContain("rows from files");
    expect(wrapper.text()).not.toContain("server");
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

  it("hides server and admin tiles from capability-only users", async () => {
    canAccessMock.mockImplementation((slug: string) => slug === "feedback");
    isSuperuserRef.value = false;

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).not.toContain("server");
    expect(wrapper.text()).not.toContain("audit logs");
  });

  function tileTitleCount(wrapper: ReturnType<typeof mountPage>, name: string): number {
    return wrapper.findAll("h3, h4").filter((heading) => heading.text().trim() === name).length;
  }

  it("shows server spoiler for superusers; utils stays pills without tile dupes", async () => {
    isSuperuserRef.value = true;

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain("server");
    expect(wrapper.text()).toContain("audit logs");
    expect(wrapper.text()).toContain("ai chat");
    expect(wrapper.findAll("details").some((el) => el.attributes("id") === "server")).toBe(true);
    expect(wrapper.get("#utils").text()).toContain("weather");
    expect(tileTitleCount(wrapper, "weather")).toBe(0);
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

  it("omits ai chat when the feature flag is off", async () => {
    vi.mocked(isAiChatEnabled).mockReturnValue(false);
    isSuperuserRef.value = true;

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain("audit logs");
    expect(wrapper.text()).not.toContain("ai chat");
  });
});

describe("tools page group order", () => {
  it("lists utils tab peers then content tiles including url-shortener", () => {
    const sections = groupServicesForToolsPage(publicToolsAsServices());
    expect(sections.map((s) => s.label)).toEqual(["utils", "content"]);
    expect(sections[0]?.services.map((tool) => tool.slug)).toEqual([
      "weather",
      "calculator",
      "password-generator",
      "qr-generator",
    ]);
    expect(sections[1]?.services.map((tool) => tool.slug)).toEqual(["recipes", "url-shortener"]);
  });

  it("excludes health-checker and vid-download from the guest public catalog", () => {
    const slugs = publicToolsAsServices().map((tool) => tool.slug);
    expect(slugs).not.toContain("health-checker");
    expect(slugs).not.toContain("vid-download");
    expect(slugs).not.toContain("expenses");
    expect(slugs).toContain("weather");
  });
});
