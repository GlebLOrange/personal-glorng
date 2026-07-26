/**
 * @vitest-environment jsdom
 */
import { mount, flushPromises } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import CallbackPage from "@/pages/CallbackPage.vue";

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  replace: vi.fn().mockResolvedValue(undefined),
  routePath: "/callback",
  routeQuery: {} as Record<string, unknown>,
  toast: vi.fn(),
  post: vi.fn(),
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ path: mocks.routePath, query: mocks.routeQuery }),
  useRouter: () => ({ push: mocks.push, replace: mocks.replace }),
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: mocks.toast }),
}));

vi.mock("@/composables/useApi", () => ({
  api: { post: mocks.post },
}));

describe("CallbackPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    mocks.replace.mockResolvedValue(undefined);
    mocks.routeQuery = { code: "oauth-code", state: "oauth-state", keep: "1" };
    mocks.post.mockResolvedValue({
      data: { github_username: "octocat", message: "GitHub linked" },
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("scrubs oauth query params and redirects to admin on success", async () => {
    const wrapper = mount(CallbackPage, {
      global: { stubs: { AuthPageShell: { template: "<div><slot /></div>" } } },
    });
    await flushPromises();

    expect(mocks.replace).toHaveBeenCalledWith({
      path: "/callback",
      query: { keep: "1" },
    });
    expect(mocks.post).toHaveBeenCalledWith("/auth/github/callback", {
      code: "oauth-code",
      state: "oauth-state",
    });
    expect(wrapper.text()).toContain("Connected as octocat");

    await vi.advanceTimersByTimeAsync(2000);
    expect(mocks.push).toHaveBeenCalledWith("/admin");
  });
});
