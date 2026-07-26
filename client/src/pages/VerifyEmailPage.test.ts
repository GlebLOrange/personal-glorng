/**
 * @vitest-environment jsdom
 */
import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

import VerifyEmailPage from "@/pages/VerifyEmailPage.vue";

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  replace: vi.fn().mockResolvedValue(undefined),
  routePath: "/verify-email",
  routeQuery: {} as Record<string, unknown>,
  post: vi.fn(),
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ path: mocks.routePath, query: mocks.routeQuery }),
  useRouter: () => ({ push: mocks.push, replace: mocks.replace }),
}));

vi.mock("@/composables/useApi", () => ({
  api: { post: mocks.post },
}));

describe("VerifyEmailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.replace.mockResolvedValue(undefined);
    mocks.routeQuery = { token: "verify-token", keep: "1" };
    mocks.post.mockResolvedValue({ data: { message: "Email verified." } });
  });

  it("scrubs token from the URL and shows success with login CTA", async () => {
    const wrapper = mount(VerifyEmailPage, {
      global: { stubs: { AuthPageShell: { template: "<div><slot /></div>" } } },
    });
    await flushPromises();

    expect(mocks.replace).toHaveBeenCalledWith({
      path: "/verify-email",
      query: { keep: "1" },
    });
    expect(mocks.post).toHaveBeenCalledWith("/auth/verify", { token: "verify-token" });
    expect(wrapper.text()).toContain("Email verified.");

    await wrapper.get("button").trigger("click");
    expect(mocks.push).toHaveBeenCalledWith("/login");
  });

  it("shows an error when token is missing", async () => {
    mocks.routeQuery = {};
    const wrapper = mount(VerifyEmailPage, {
      global: { stubs: { AuthPageShell: { template: "<div><slot /></div>" } } },
    });
    await flushPromises();

    expect(mocks.post).not.toHaveBeenCalled();
    expect(wrapper.text()).toContain("Missing verification token.");
  });
});
