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
}));

const routerLinkStub = {
  props: ["to"],
  template: "<a :href=\"typeof to === 'string' ? to : '#'\"><slot /></a>",
};

describe("NotFoundPage", () => {
  it("shows the heading, requested path, and recovery links", () => {
    mocks.fullPath = "/this-does-not-exist";
    const wrapper = mount(NotFoundPage, {
      global: {
        stubs: { RouterLink: routerLinkStub },
      },
    });

    expect(wrapper.get("h1").text()).toBe("This path isn't on Gleb.Y.");
    expect(wrapper.text()).toContain("404");
    expect(wrapper.text()).toContain("/this-does-not-exist");

    const hrefs = wrapper.findAll("a").map((link) => link.attributes("href"));
    expect(hrefs).toContain("/");
    expect(hrefs).toContain("/#experience");
    expect(hrefs).toContain("/tools");
    expect(hrefs).toContain("/news");
    expect(wrapper.text()).toContain("experience");
    expect(wrapper.text()).toContain("tools");
    expect(wrapper.text()).toContain("news");
    expect(wrapper.text()).not.toMatch(/\bExperience\b/);
    expect(wrapper.text()).not.toMatch(/\bTools\b/);
    expect(wrapper.text()).not.toMatch(/\bNews\b/);
  });

  it.each([
    ["/pricing", "No public price list here.", "Compensation is role- and contract-specific"],
    ["/rates", "No public price list here.", "Compensation is role- and contract-specific"],
    ["/terms", "No public terms page.", "personal portfolio"],
    ["/tos", "No public terms page.", "personal portfolio"],
    ["/signup", "Signup isn't open.", "no public registration"],
    ["/register", "Signup isn't open.", "no public registration"],
  ] as const)("shows warm copy for %s", (path, title, bodySnippet) => {
    mocks.fullPath = path;
    const wrapper = mount(NotFoundPage, {
      global: {
        stubs: { RouterLink: routerLinkStub },
      },
    });

    expect(wrapper.get("h1").text()).toBe(title);
    expect(wrapper.text()).toContain(bodySnippet);
    expect(wrapper.text()).toContain(path);
  });

  it("offers privacy recovery for terms paths", () => {
    mocks.fullPath = "/terms";
    const wrapper = mount(NotFoundPage, {
      global: {
        stubs: { RouterLink: routerLinkStub },
      },
    });

    const hrefs = wrapper.findAll("a").map((link) => link.attributes("href"));
    expect(hrefs).toContain("/privacy");
  });
});
