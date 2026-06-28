import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import NewsRoutePage from "@/pages/NewsRoutePage.vue";

const mocks = vi.hoisted(() => ({
  isSuperuser: { value: false },
}));

vi.mock("@/composables/usePermissions", () => ({
  usePermissions: () => ({ isSuperuser: mocks.isSuperuser }),
}));

vi.mock("@/pages/NewsPage.vue", () => ({
  __isKeepAlive: false,
  __isTeleport: false,
  __isSuspense: false,
  name: "NewsPage",
  default: { template: '<section data-testid="public-news" />' },
}));

vi.mock("@/pages/admin/tools/NewsAdminPage.vue", () => ({
  __isKeepAlive: false,
  __isTeleport: false,
  __isSuspense: false,
  name: "NewsAdminPage",
  default: { template: '<section data-testid="admin-news" />' },
}));

describe("NewsRoutePage", () => {
  it("shows the public news page for non-superusers", async () => {
    mocks.isSuperuser.value = false;
    const wrapper = mount(NewsRoutePage);

    await flushPromises();

    expect(wrapper.find('[data-testid="public-news"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="admin-news"]').exists()).toBe(false);
  });

  it("shows the admin news page for superusers", async () => {
    mocks.isSuperuser.value = true;
    const wrapper = mount(NewsRoutePage);

    await flushPromises();

    expect(wrapper.find('[data-testid="admin-news"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="public-news"]').exists()).toBe(false);
  });
});
