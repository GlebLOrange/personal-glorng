import { flushPromises, mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ToolsPage from "@/pages/ToolsPage.vue";
import { groupServicesByCategory, publicToolsAsServices } from "@/platform/services";
import { useAuthStore } from "@/stores/auth";
import type { UserResponse } from "@/types";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";

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

vi.mock("@/utils/featureFlags", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/utils/featureFlags")>();
  return {
    ...actual,
    isAiChatEnabled: vi.fn(() => true),
  };
});

import { isAiChatEnabled } from "@/utils/featureFlags";

function makeUser(permissions: string[]): UserResponse {
  return {
    id: "1",
    email: "a@b.c",
    permissions,
    is_verified: true,
    display_name: "User",
    timezone: "UTC",
    preferences: {},
    created_at: "2026-01-01T00:00:00Z",
  };
}

describe("ToolsPage sectioned layout", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    useRouteMock.mockReturnValue({ query: {} });
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

  it("shows all category headings and tiles without tabs", async () => {
    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.findAll('[role="tab"]')).toHaveLength(0);
    expect(wrapper.text()).toContain("content");
    expect(wrapper.text()).toContain("utilities");
    expect(wrapper.text()).toContain("recipes");
    expect(wrapper.text()).toContain("calculator");
    expect(wrapper.text()).toContain("Shorten a long link.");
    expect(wrapper.text()).toContain("Do a quick calculation.");
    // expenses (only public productivity tool) is off by default via feature flag
    expect(wrapper.text()).not.toContain("expenses");
    expect(wrapper.text()).not.toContain("productivity");
    expect(wrapper.text()).not.toContain("news");
    expect(wrapper.findAll("h2").some((h) => h.text() === "admin")).toBe(false);
    expect(wrapper.text()).not.toContain("audit logs");
    expect(wrapper.get('[data-testid="crumbs"]').text()).toBe("tools");
    // Public presentation hides the visible count badge (sr-only count remains).
    const contentHeading = wrapper.findAll("h2").find((h) => h.text().includes("content"));
    expect(contentHeading?.find("[aria-hidden=\"true\"]").exists()).toBe(false);
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
    const auth = useAuthStore();
    auth.user = makeUser(["feedback:read"]);

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.findAll("h2").some((h) => h.text() === "admin")).toBe(false);
    expect(wrapper.text()).not.toContain("audit logs");
  });

  it("shows admin hub tiles for superusers", async () => {
    const auth = useAuthStore();
    auth.user = makeUser([SUPERUSER_PERMISSION]);

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.findAll("h2").some((h) => h.text() === "admin")).toBe(true);
    expect(wrapper.text()).toContain("audit logs");
    expect(wrapper.text()).toContain("ai chat");
  });

  it("omits ai chat from admin tiles when the feature flag is off", async () => {
    vi.mocked(isAiChatEnabled).mockReturnValue(false);
    const auth = useAuthStore();
    auth.user = makeUser([SUPERUSER_PERMISSION]);

    const wrapper = mountPage();
    await flushPromises();

    expect(wrapper.findAll("h2").some((h) => h.text() === "admin")).toBe(true);
    expect(wrapper.text()).toContain("audit logs");
    expect(wrapper.text()).not.toContain("ai chat");
  });
});

describe("tools content tile order", () => {
  /** Mirrors PUBLIC_TILE_ORDER usefulness ranking in ToolsPage.vue. */
  const PUBLIC_TILE_ORDER = [
    "weather",
    "url-shortener",
    "recipes",
    "calculator",
    "password-generator",
    "qr-generator",
  ];

  function sortPublicTools<T extends { slug: string }>(tools: T[]): T[] {
    return [...tools].sort((a, b) => {
      const ai = PUBLIC_TILE_ORDER.indexOf(a.slug);
      const bi = PUBLIC_TILE_ORDER.indexOf(b.slug);
      if (ai === -1 && bi === -1) return 0;
      if (ai === -1) return 1;
      if (bi === -1) return -1;
      return ai - bi;
    });
  }

  it("lists url-shortener before recipes in the content section", () => {
    const content = groupServicesByCategory(
      sortPublicTools(publicToolsAsServices()),
    ).find((section) => section.category === "content");
    expect(content?.services.map((tool) => tool.slug)).not.toContain("news");
    expect(content?.services.map((tool) => tool.slug)).toEqual([
      "url-shortener",
      "recipes",
    ]);
  });

  it("lists utilities in usefulness order", () => {
    const utilities = groupServicesByCategory(
      sortPublicTools(publicToolsAsServices()),
    ).find((section) => section.category === "utilities");
    expect(utilities?.services.map((tool) => tool.slug)).toEqual([
      "weather",
      "calculator",
      "password-generator",
      "qr-generator",
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
