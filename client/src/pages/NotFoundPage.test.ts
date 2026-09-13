/**
 * @vitest-environment jsdom
 */
import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import NotFoundPage from "@/pages/NotFoundPage.vue";

const mocks = vi.hoisted(() => ({
  fullPath: "/this-does-not-exist",
}));

vi.mock("vue-router", () => ({
  useRoute: () => ({ fullPath: mocks.fullPath }),
  RouterLink: {
    props: ["to"],
    template: "<a :href=\"typeof to === 'string' ? to : '#'\"><slot /></a>",
  },
}));

describe("NotFoundPage", () => {
  it("shows the heading, requested path, and recovery links", () => {
    mocks.fullPath = "/this-does-not-exist";
    const wrapper = mount(NotFoundPage);

    expect(wrapper.get("h1").text()).toBe("This path isn't on Gleb.Y.");
    expect(wrapper.text()).toContain("404");
    expect(wrapper.text()).toContain("/this-does-not-exist");

    const hrefs = wrapper.findAll("a").map((link) => link.attributes("href"));
    expect(hrefs).toContain("/");
    expect(hrefs).toContain("/tools");
    expect(hrefs).toContain("/news");
  });
});
