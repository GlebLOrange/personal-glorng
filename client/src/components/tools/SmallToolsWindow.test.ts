/**
 * @vitest-environment jsdom
 */
import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter, type Router } from "vue-router";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { defineComponent, h } from "vue";

import SmallToolsWindow from "@/components/tools/SmallToolsWindow.vue";
import { WEATHER_ROUTE_NAME } from "@/constants/weather";
import { useAuthStore } from "@/stores/auth";

const StubPage = defineComponent({
  name: "StubPage",
  setup() {
    return () => h("div", { "data-testid": "stub-page" }, "tool body");
  },
});

vi.mock("@/components/layout/PinnedToolsRow.vue", () => ({
  default: { template: '<div data-testid="pinned-row" />' },
}));

vi.mock("@/composables/usePermissions", () => ({
  usePermissions: () => ({
    canAccess: (slug: string) => slug === "email" || slug === "vid-download",
    can: () => true,
    isSuperuser: { value: false },
    permissions: { value: [] },
    canUseAdminHub: { value: false },
  }),
}));

async function mountWindow(
  initialPath: string,
  authenticated: boolean,
): Promise<{ wrapper: ReturnType<typeof mount>; router: Router }> {
  const pinia = createPinia();
  setActivePinia(pinia);
  const auth = useAuthStore();
  auth.sessionResolved = true;
  auth.user = authenticated
    ? ({
        id: 1,
        email: "op@example.com",
        display_name: "op",
        is_active: true,
        permissions: ["email:write", "vid-download:read"],
      } as never)
    : null;

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        component: SmallToolsWindow,
        children: [
          {
            path: "/weather",
            name: WEATHER_ROUTE_NAME,
            component: StubPage,
            meta: { title: "Weather" },
          },
          {
            path: "/calculator",
            name: "calculator",
            component: StubPage,
            meta: { title: "Calculator" },
          },
          {
            path: "/password-generator",
            name: "password-generator",
            component: StubPage,
            meta: { title: "Password generator" },
          },
          {
            path: "/qr-generator",
            name: "qr-generator",
            component: StubPage,
            meta: { title: "QR generator" },
          },
          {
            path: "/vid-download",
            name: "vid-download",
            component: StubPage,
            meta: { title: "Video downloader" },
          },
          {
            path: "/tools/send-email",
            name: "tool-email",
            component: StubPage,
            meta: { title: "Send email" },
          },
        ],
      },
      { path: "/tools", name: "tools", component: StubPage },
    ],
  });

  await router.push(initialPath);
  await router.isReady();

  const wrapper = mount(defineComponent({ template: "<RouterView />" }), {
    global: {
      plugins: [pinia, router],
      stubs: {
        BackLink: { template: '<a href="/tools" aria-label="back">back</a>' },
      },
    },
  });

  await flushPromises();
  return { wrapper, router };
}

describe("SmallToolsWindow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("marks the active tab from the current route", async () => {
    const { wrapper } = await mountWindow("/calculator", false);

    const selected = wrapper.get('[role="tab"][aria-selected="true"]');
    expect(selected.text()).toBe("calculator");
    expect(selected.attributes("id")).toBe("small-tools-tab-calculator");
    expect(wrapper.get("h1").text()).toContain("Calculator");

    wrapper.unmount();
  });

  it("shows the same four utils tabs for guests and signed-in users", async () => {
    const guest = await mountWindow("/weather", false);
    const guestLabels = guest.wrapper.findAll('[role="tab"]').map((tab) => tab.text());
    expect(guestLabels).toEqual([
      "weather",
      "calculator",
      "password generator",
      "qr generator",
    ]);
    expect(guestLabels).not.toContain("video downloader");
    expect(guestLabels).not.toContain("send email");
    guest.wrapper.unmount();

    const signedIn = await mountWindow("/weather", true);
    const signedInLabels = signedIn.wrapper.findAll('[role="tab"]').map((tab) => tab.text());
    expect(signedInLabels).toEqual(guestLabels);
    signedIn.wrapper.unmount();
  });

  it("sizes the tool panel to max-w-sm and h-[28rem]", async () => {
    const { wrapper } = await mountWindow("/calculator", false);

    const panel = wrapper.get('[role="tabpanel"]');
    expect(panel.classes()).toContain("h-[28rem]");
    expect(panel.classes()).toContain("max-h-[calc(100dvh-16rem)]");
    expect(panel.classes()).not.toContain("h-[32rem]");
    expect(wrapper.find(".max-w-sm").exists()).toBe(true);
    expect(wrapper.find(".max-w-md").exists()).toBe(false);

    wrapper.unmount();
  });

  it("switches route on arrow key navigation", async () => {
    const { wrapper, router } = await mountWindow("/weather", false);

    const first = wrapper.get('[role="tab"]');
    await first.trigger("keydown", { key: "ArrowRight" });
    await flushPromises();

    expect(router.currentRoute.value.name).toBe("calculator");

    wrapper.unmount();
  });
});
