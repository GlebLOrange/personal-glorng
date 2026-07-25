import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "@/App.vue";
import { useAuthStore } from "@/stores/auth";

describe("App", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("mounts a global toast host outside PageShell", () => {
    const wrapper = mount(App, {
      global: {
        stubs: {
          RouterView: true,
          NavBar: true,
          FooterBar: true,
          ScrollControls: true,
          ToastContainer: {
            name: "ToastContainer",
            template: '<div data-testid="toast-host" />',
          },
        },
      },
    });

    expect(wrapper.find('[data-testid="toast-host"]').exists()).toBe(true);
  });

  it("surfaces sessionError with retry", async () => {
    const auth = useAuthStore();
    auth.sessionError = "Unable to restore session";
    const resolveSession = vi.spyOn(auth, "resolveSession").mockResolvedValue();

    const wrapper = mount(App, {
      global: {
        stubs: {
          RouterView: true,
          NavBar: true,
          FooterBar: true,
          ScrollControls: true,
          ToastContainer: true,
        },
      },
    });

    expect(wrapper.text()).toContain("Unable to restore session");
    await wrapper.get("button").trigger("click");
    expect(resolveSession).toHaveBeenCalledOnce();
  });
});
