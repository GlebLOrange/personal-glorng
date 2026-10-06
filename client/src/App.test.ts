import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { createMemoryHistory, createRouter } from "vue-router";

import App from "@/App.vue";
import { useAuthStore } from "@/stores/auth";

async function mountApp(path = "/") {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: { template: "<div />" } },
      { path: "/login", component: { template: "<div />" }, meta: { noindex: true } },
      {
        path: "/admin",
        component: { template: "<div />" },
        meta: { requiresAuth: true, noindex: true },
      },
    ],
  });
  await router.push(path);
  await router.isReady();

  return mount(App, {
    global: {
      plugins: [router],
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
}

describe("App", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("mounts a global toast host outside PageShell", async () => {
    const wrapper = await mountApp("/");
    expect(wrapper.find('[data-testid="toast-host"]').exists()).toBe(true);
  });

  it("hides sessionError on public pages", async () => {
    const auth = useAuthStore();
    auth.sessionError = "Unable to restore session";

    const wrapper = await mountApp("/");
    expect(wrapper.text()).not.toContain("Unable to restore session");
  });

  it("surfaces sessionError with retry on login", async () => {
    const auth = useAuthStore();
    auth.sessionError = "Unable to restore session";
    const resolveSession = vi.spyOn(auth, "resolveSession").mockResolvedValue();

    const wrapper = await mountApp("/login");

    expect(wrapper.text()).toContain("Unable to restore session");
    await wrapper.get("button").trigger("click");
    expect(resolveSession).toHaveBeenCalledOnce();
  });
});
