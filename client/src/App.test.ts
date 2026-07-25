import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import App from "@/App.vue";

describe("App", () => {
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
});
