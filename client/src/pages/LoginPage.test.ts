import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import LoginPage from "@/pages/LoginPage.vue";

vi.mock("@/constants/firebase", () => ({
  isFirebaseEnabled: true,
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ query: {} }),
  useRouter: () => ({ push: vi.fn() }),
  RouterLink: {
    props: ["to"],
    template: "<a><slot /></a>",
  },
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: vi.fn() }),
}));

describe("LoginPage", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("shows email password login and Google sign-in", () => {
    const wrapper = mount(LoginPage);

    expect(wrapper.get('input[type="email"]').exists()).toBe(true);
    expect(wrapper.get('input[type="password"]').exists()).toBe(true);
    expect(wrapper.text()).toContain("Login");
    expect(wrapper.text()).toContain("Continue with Google");
  });
});
