import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import NewsRoutePage from "@/pages/NewsRoutePage.vue";

vi.mock("@/pages/NewsPage.vue", () => ({
  __isKeepAlive: false,
  __isTeleport: false,
  __isSuspense: false,
  name: "NewsPage",
  default: { template: '<section data-testid="public-news" />' },
}));

describe("NewsRoutePage", () => {
  it("always shows the public news digest", async () => {
    const wrapper = mount(NewsRoutePage);

    await flushPromises();

    expect(wrapper.find('[data-testid="public-news"]').exists()).toBe(true);
  });
});
