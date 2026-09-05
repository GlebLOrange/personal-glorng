/**
 * @vitest-environment jsdom
 */
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ResetPasswordPage from "@/pages/ResetPasswordPage.vue";

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  replace: vi.fn().mockResolvedValue(undefined),
  routePath: "/reset-password",
  routeQuery: {} as Record<string, unknown>,
  toast: vi.fn(),
  post: vi.fn(),
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ path: mocks.routePath, query: mocks.routeQuery }),
  useRouter: () => ({ push: mocks.push, replace: mocks.replace }),
  RouterLink: {
    props: ["to"],
    template: "<a :href=\"typeof to === 'string' ? to : '#'\"><slot /></a>",
  },
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: mocks.toast }),
}));

vi.mock("@/composables/useApi", () => ({
  api: { post: mocks.post },
}));

describe("ResetPasswordPage", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    mocks.replace.mockResolvedValue(undefined);
    mocks.routeQuery = { token: "secret-token", keep: "1" };
  });

  it("scrubs token from the URL while keeping the form usable", async () => {
    const wrapper = mount(ResetPasswordPage, {
      global: { stubs: { AuthPageShell: { template: "<div><slot /></div>" } } },
    });
    await flushPromises();

    expect(mocks.replace).toHaveBeenCalledWith({
      path: "/reset-password",
      query: { keep: "1" },
    });
    expect(wrapper.find("form").exists()).toBe(true);
    expect(wrapper.text()).not.toContain("Invalid or missing reset link");
  });
});
