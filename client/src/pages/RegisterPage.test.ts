/**
 * @vitest-environment jsdom
 */
import { mount, flushPromises } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import RegisterPage from "@/pages/RegisterPage.vue";
import { useAuthStore } from "@/stores/auth";

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  toast: vi.fn(),
}));

vi.mock("vue-router", () => ({
  useRouter: () => ({ push: mocks.push }),
  RouterLink: {
    props: ["to"],
    template: "<a :href=\"typeof to === 'string' ? to : '#'\"><slot /></a>",
  },
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: mocks.toast }),
}));

describe("RegisterPage", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  function mountPage() {
    return mount(RegisterPage, {
      global: {
        stubs: {
          AuthPageShell: { template: "<div><slot /></div>" },
          RouterLink: { template: "<a><slot /></a>" },
        },
      },
    });
  }

  it("shows registration fields", () => {
    const wrapper = mountPage();
    expect(wrapper.get('input[type="email"]').exists()).toBe(true);
    expect(wrapper.findAll('input[type="password"]').length).toBeGreaterThanOrEqual(1);
    expect(wrapper.text().toLowerCase()).toContain("create account");
  });

  it("shows success status and navigates to login after register", async () => {
    const wrapper = mountPage();
    const auth = useAuthStore();
    vi.spyOn(auth, "register").mockResolvedValue();

    await wrapper.get('input[type="email"]').setValue("new@example.com");
    const passwords = wrapper.findAll('input[type="password"]');
    await passwords[0]!.setValue("MyTestPass123!");
    await passwords[1]!.setValue("MyTestPass123!");
    const terms = wrapper.find('input[type="checkbox"]');
    if (terms.exists()) await terms.setValue(true);
    await wrapper.get("form").trigger("submit");
    await flushPromises();

    expect(auth.register).toHaveBeenCalled();
    expect(wrapper.text()).toContain("We sent a verification link");
    expect(wrapper.text()).toContain("new@example.com");
    expect(mocks.toast).toHaveBeenCalledWith("Check your email to verify your account", "success");

    const loginBtn = wrapper.findAll("button").find((b) => b.text().includes("go to login"));
    expect(loginBtn).toBeDefined();
    await loginBtn!.trigger("click");
    expect(mocks.push).toHaveBeenCalledWith("/login");
  });
});
