/**
 * @vitest-environment jsdom
 */
import { mount, flushPromises } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ForgotPasswordPage from "@/pages/ForgotPasswordPage.vue";

const mocks = vi.hoisted(() => ({
  toast: vi.fn(),
  post: vi.fn(),
}));

vi.mock("vue-router", () => ({
  RouterLink: {
    props: ["to"],
    template: '<a :href="typeof to === \'string\' ? to : \'#\'"><slot /></a>',
  },
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: mocks.toast }),
}));

vi.mock("@/composables/useApi", () => ({
  api: { post: mocks.post },
}));

describe("ForgotPasswordPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.post.mockResolvedValue({ data: {} });
  });

  it("shows confirmation after a successful submit", async () => {
    const wrapper = mount(ForgotPasswordPage, {
      global: { stubs: { AuthPageShell: { template: "<div><slot /></div>" } } },
    });

    await wrapper.get('input[type="email"]').setValue("user@example.com");
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(mocks.post).toHaveBeenCalledWith("/auth/forgot-password", {
      email: "user@example.com",
    });
    expect(wrapper.text().toLowerCase()).toMatch(/reset|email|sent|check/);
    expect(wrapper.find("form").exists()).toBe(false);
  });
});
