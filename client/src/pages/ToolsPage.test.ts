import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { computed, ref } from "vue";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ToolsPage from "@/pages/ToolsPage.vue";
import { publicToolsAsServices } from "@/platform/services";
import { groupServicesForToolsPage } from "@/utils/toolsPageGroups";

const replaceMock = vi.fn();
const useRouteMock = vi.fn(() => ({ query: {} as Record<string, string> }));
const canAccessMock = vi.fn((_slug: string) => false);
const isSuperuserRef = ref(false);

vi.mock("vue-router", () => ({
  useRoute: () => useRouteMock(),
  useRouter: () => ({ replace: replaceMock }),
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

function stubDesktopViewport(): void {
  vi.stubGlobal(
    "matchMedia",
    vi.fn((query: string) => ({
      matches: false, // not max-width:767px → desktop defaults open
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  );
}

function stubMobileViewport(): void {
  vi.stubGlobal(
    "matchMedia",
    vi.fn((query: string) => ({
      matches: query.includes("max-width"),
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  );
}

describe("ToolsPage spoiler catalog", () => {
  beforeEach(() => {
    sessionStorage.clear();
    replaceMock.mockClear();
    setActivePinia(createPinia());
    useRouteMock.mockReturnValue({ query: {} });
    canAccessMock.mockReturnValue(false);
    isSuperuserRef.value = false;
    vi.mocked(isAiChatEnabled).mockReturnValue(true);
    stubDesktopViewport();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function mountPage(options: { attachTo?: HTMLElement } = {}) {
    return mount(ToolsPage, {
      ...options,
      global: {
        stubs: {
          PageShell: {
            props: ["title", "breadcrumbs", "backTo", "narrow", "bodyWidth"],
            template:
              '<div><div data-testid="crumbs"><span v-for="(c, i) in breadcrumbs" :key="i">{{ c.label }}</span></div><slot /></div>',
          },
        },
      },
    });
  }

  function tileTitleCount(wrapper: ReturnType<typeof mountPage>, name: string): number {
    return wrapper.findAll("h3, h4").filter((heading) => heading.text().trim() === name).length;
  }

  it("shows static utils pills and open content spoilers for guests", async () => {
    const wrapper = mountPage();
    await flushPromises();

    const utils = wrapper.get("#utils");
    expect(utils.element.tagName.toLowerCase()).toBe("details");
    expect(utils.attributes("open")).toBeDefined();
    expect(utils.text()).toContain("▸");
    expect(utils.get("summary [data-section-label]").text()).toBe("utils");
    expect(utils.find("summary h2").exists()).toBe(false);
    expect(utils.get('[aria-label="utils tools"] li a').attributes("title")).toBeUndefined();
    expect(utils.get('[aria-label="utils tools"] li a').classes()).toContain("min-h-11");
    expect(utils.findAll('[aria-label="utils tools"] li').length).toBe(5);
    expect(utils.text()).toContain("quick math");
    const pills = utils.get('[aria-label="utils tools"]');
    expect(pills.exists()).toBe(true);
    expect(pills.text()).toContain("weather");
    expect(pills.text()).toContain("calculator");
    expect(pills.text()).toContain("password generator");
    expect(pills.text()).toContain("qr generator");
    expect(pills.text()).toContain("url shortener");
    expect(pills.text()).not.toContain("demo");
    // Guest utils: weather, calculator, password-generator, qr-generator, url-shortener.
    expect(pills.findAll("svg.tool-icon")).toHaveLength(5);
    expect(tileTitleCount(wrapper, "url shortener")).toBe(0);
    expect(utils.text()).not.toContain("video downloader");
    expect(utils.text()).not.toContain("send email");
    expect(wrapper.text()).not.toContain("health");

    const spoilers = wrapper.findAll("details");
    expect(spoilers.length).toBeGreaterThanOrEqual(1);
    expect(spoilers.every((el) => el.attributes("open") !== undefined)).toBe(true);
    expect(spoilers.some((el) => el.attributes("id") === "utils")).toBe(true);
    const ids = wrapper.findAll("[id]").map((el) => el.attributes("id"));
    expect(new Set(ids).size).toBe(ids.length);
    expect(wrapper.findAll("summary [data-section-label]").length).toBe(spoilers.length);

    expect(wrapper.text()).toContain("content");
    expect(wrapper.text()).toContain("recipes");
    expect(wrapper.get("#content").text()).toContain("recipes");
    expect(tileTitleCount(wrapper, "recipes")).toBe(1);
    expect(wrapper.get("#content").text()).toContain("demo");
    expect(wrapper.get("#content").text()).not.toContain("url shortener");
    expect(wrapper.text()).not.toContain("server");
    expect(wrapper.text()).not.toContain("expenses");
    expect(wrapper.text()).not.toContain("Everyday");
    expect(wrapper.get('[data-testid="crumbs"]').text()).toBe("tools");
  });

  it("shows video as a utils pill when authenticated with access", async () => {
    canAccessMock.mockImplementation((slug: string) => slug === "vid-download");

    const wrapper = mountPage();
    await flushPromises();

    const pills = wrapper.get("#utils").get('[aria-label="utils tools"]');
    expect(pills.text()).toContain("video downloader");
    expect(wrapper.find("#content").exists()).toBe(true);
    expect(wrapper.get("#content").text()).not.toContain("video downloader");
    expect(tileTitleCount(wrapper, "video downloader")).toBe(0);
  });

  it("shows file share and data extract as utils pills and yours on content cards", async () => {
    canAccessMock.mockImplementation((slug: string) =>
      ["tasks", "file-share", "data-extract"].includes(slug),
    );
    const wrapper = mountPage();
    await flushPromises();

    const pills = wrapper.get("#utils").get('[aria-label="utils tools"]');
    expect(pills.text()).toContain("file share");
    expect(pills.text()).toContain("data extract");
    expect(wrapper.get("#content").text()).toContain("yours");
    expect(wrapper.get("#content").text()).toContain("tasks and reminders");
    expect(wrapper.get("#utils").text()).not.toContain("yours");
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

  it("dismissing a notice drops its query key", async () => {
    useRouteMock.mockReturnValue({ query: { expenses: "off", tab: "x" } });
    const wrapper = mountPage();
    await flushPromises();
    await wrapper.get('[data-notice="expenses"] button').trigger("click");
    expect(replaceMock).toHaveBeenCalledWith({ query: { tab: "x" } });
  });

  it("hides server and admin tiles from capability-only users", async () => {
    canAccessMock.mockImplementation((slug: string) => slug === "feedback");
    isSuperuserRef.value = false;

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).not.toContain("server");
    expect(wrapper.text()).not.toContain("audit logs");
  });

  it("shows server spoiler for superusers; utils stays pills without tile dupes", async () => {
    isSuperuserRef.value = true;

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.text()).toContain("server");
    expect(wrapper.text()).toContain("audit logs");
    expect(wrapper.get("#utils").get('[aria-label="utils tools"]').text()).toContain("ai chat");
    expect(wrapper.get("#utils").get('[aria-label="utils tools"]').text()).toContain("send email");
    expect(wrapper.findAll("details").some((el) => el.attributes("id") === "server")).toBe(true);
    expect(wrapper.get("#server").text()).toContain("health");
    expect(wrapper.get("#utils").text()).toContain("weather");
    expect(tileTitleCount(wrapper, "weather")).toBe(0);
    expect(tileTitleCount(wrapper, "url shortener")).toBe(0);
    expect(tileTitleCount(wrapper, "ai chat")).toBe(0);
    expect(tileTitleCount(wrapper, "email")).toBe(0);
    expect(wrapper.get("#utils").text()).toContain("url shortener");
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

  it("collapses sections by default on mobile viewports", async () => {
    stubMobileViewport();
    const wrapper = mountPage();
    await flushPromises();
    const spoilers = wrapper.findAll("details");
    expect(spoilers.length).toBeGreaterThanOrEqual(1);
    expect(wrapper.get("#utils").attributes("open")).toBeDefined();
    expect(
      spoilers
        .filter((el) => el.attributes("id") !== "utils")
        .every((el) => el.attributes("open") === undefined),
    ).toBe(true);
  });

  it("allows several sections open at once on mobile", async () => {
    stubMobileViewport();
    isSuperuserRef.value = true;
    canAccessMock.mockImplementation(() => true);
    const wrapper = mountPage();
    await flushPromises();
    const spoilers = wrapper.findAll("details");
    expect(spoilers.length).toBeGreaterThanOrEqual(2);
    const [first, second] = spoilers as [(typeof spoilers)[number], (typeof spoilers)[number]];
    (first.element as HTMLDetailsElement).open = true;
    await first.trigger("toggle");
    (second.element as HTMLDetailsElement).open = true;
    await second.trigger("toggle");
    await flushPromises();
    expect(first.attributes("open")).toBeDefined();
    expect(second.attributes("open")).toBeDefined();
  });

  it("remembers opened sections per viewport band in sessionStorage", async () => {
    sessionStorage.clear();
    stubMobileViewport();
    isSuperuserRef.value = true;
    canAccessMock.mockImplementation(() => true);
    const first = mountPage();
    await flushPromises();
    const utils = first.get("#utils");
    (utils.element as HTMLDetailsElement).open = false;
    await utils.trigger("toggle");
    expect(JSON.parse(sessionStorage.getItem("tools:open-sections:narrow") ?? "{}")).toMatchObject({
      utils: false,
    });
    first.unmount();

    const second = mountPage();
    await flushPromises();
    expect(second.get("#utils").attributes("open")).toBeUndefined();
    sessionStorage.clear();
  });

  it("does not rewrite the URL hash when sections open or close", async () => {
    stubMobileViewport();
    const wrapper = mountPage();
    await flushPromises();
    replaceMock.mockClear();
    const utils = wrapper.get("#utils");
    (utils.element as HTMLDetailsElement).open = true;
    await utils.trigger("toggle");
    (utils.element as HTMLDetailsElement).open = false;
    await utils.trigger("toggle");
    expect(replaceMock).not.toHaveBeenCalled();
  });

  it("opens the section named by an inbound #hash", async () => {
    stubMobileViewport();
    useRouteMock.mockReturnValue({ query: {}, hash: "#utils" });
    const wrapper = mountPage();
    await flushPromises();
    expect(wrapper.get("#utils").attributes("open")).toBeDefined();
  });
});

describe("tools page group order", () => {
  it("lists utils tab peers and url-shortener then content recipes", () => {
    const sections = groupServicesForToolsPage(publicToolsAsServices());
    expect(sections.map((s) => s.label)).toEqual(["utils", "content"]);
    expect(sections[0]?.services.map((tool) => tool.slug)).toEqual([
      "weather",
      "calculator",
      "password-generator",
      "qr-generator",
      "url-shortener",
    ]);
    expect(sections[1]?.services.map((tool) => tool.slug)).toEqual(["recipes"]);
  });

  it("excludes health-checker and vid-download from the guest public catalog", () => {
    const slugs = publicToolsAsServices().map((tool) => tool.slug);
    expect(slugs).not.toContain("health-checker");
    expect(slugs).not.toContain("vid-download");
    expect(slugs).not.toContain("expenses");
    expect(slugs).toContain("weather");
  });
});
