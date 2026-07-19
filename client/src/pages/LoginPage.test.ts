import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import LoginPage from "@/pages/LoginPage.vue";
import { useAuthStore } from "@/stores/auth";

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  routeQuery: {} as Record<string, unknown>,
  toast: vi.fn(),
}));

vi.mock("@/constants/firebase", () => ({
  isFirebaseEnabled: true,
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ query: mocks.routeQuery }),
  useRouter: () => ({ push: mocks.push }),
  RouterLink: {
    props: ["to"],
    template: "<a><slot /></a>",
  },
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: mocks.toast }),
}));

describe("LoginPage", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    mocks.routeQuery = {};
  });

  it("shows email password login and Google sign-in", () => {
    const wrapper = mount(LoginPage);

    expect(wrapper.get('input[type="email"]').attributes("placeholder")).toBe("you@example.com");
    expect(wrapper.get('input[type="password"]').exists()).toBe(true);
    expect(wrapper.text()).toContain("login");
    expect(wrapper.text()).toContain("continue with Google");
    expect(wrapper.text()).toContain("create account");
    expect(wrapper.text()).toContain("forgot password?");
  });

  it("submits credentials and redirects after login", async () => {
    mocks.routeQuery.redirect = "/admin";
    const wrapper = mount(LoginPage);
    const auth = useAuthStore();
    const login = vi.spyOn(auth, "login").mockResolvedValue();

    await wrapper.get('input[type="email"]').setValue("admin@example.com");
    await wrapper.get('input[type="password"]').setValue("password-123");
    await wrapper.get("form").trigger("submit");

    expect(login).toHaveBeenCalledWith("admin@example.com", "password-123");
    await vi.waitFor(() => expect(mocks.push).toHaveBeenCalledWith("/admin"));
    expect(mocks.toast).toHaveBeenCalledWith("Logged in successfully", "success");
  });
});
