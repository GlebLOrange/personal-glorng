import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import PageBreadcrumbs from "@/components/layout/PageBreadcrumbs.vue";

const routerLinkStub = {
  props: ["to"],
  template: '<a :href="typeof to === \'string\' ? to : to.path" v-bind="$attrs"><slot /></a>',
};

describe("PageBreadcrumbs", () => {
  it("renders plain labels with muted ancestors and highlighted current", () => {
    const wrapper = mount(PageBreadcrumbs, {
      props: {
        segments: [{ label: "admin", to: "/admin" }, { label: "app logs" }],
        elevated: true,
      },
      global: {
        stubs: { RouterLink: routerLinkStub },
      },
    });

    expect(wrapper.get("a").attributes("href")).toBe("/admin");
    expect(wrapper.get("a span").text()).toBe("admin");
    expect(wrapper.get("a span").classes()).toContain("text-surface-mid");
    expect(wrapper.get("a span").classes()).not.toContain("accent-gradient");

    const current = wrapper.get("[aria-current=page]");
    expect(current.text()).toBe("app logs");
    expect(current.classes()).toContain("text-surface-light");
    expect(current.classes()).toContain("text-xl");
    expect(current.classes()).not.toContain("accent-gradient");
    expect(wrapper.text()).toMatch(/admin\s*\/\s*app logs/);
  });

  it("keeps elevated current crumb as a link when to is set", () => {
    const wrapper = mount(PageBreadcrumbs, {
      props: {
        segments: [{ label: "admin", to: "/admin" }],
        elevated: true,
      },
      global: {
        stubs: { RouterLink: routerLinkStub },
      },
    });

    const current = wrapper.get("[aria-current=page]");
    expect(current.element.tagName).toBe("A");
    expect(current.attributes("href")).toBe("/admin");
    expect(current.get("span").text()).toBe("admin");
    expect(current.get("span").classes()).toContain("text-surface-light");
    expect(current.get("span").classes()).toContain("text-xl");
    expect(current.get("span").classes()).not.toContain("accent-gradient");
  });

  it("highlights current without elevated title scale", () => {
    const wrapper = mount(PageBreadcrumbs, {
      props: {
        segments: [{ label: "tools", to: "/tools" }, { label: "calculator" }],
        elevated: false,
      },
      global: {
        stubs: { RouterLink: routerLinkStub },
      },
    });

    const current = wrapper.get("[aria-current=page]");
    expect(current.text()).toBe("calculator");
    expect(current.classes()).toContain("font-medium");
    expect(current.classes()).toContain("text-surface-light");
    expect(current.classes()).not.toContain("accent-gradient");
  });

  it("links the current category crumb when to is provided", () => {
    const wrapper = mount(PageBreadcrumbs, {
      props: {
        segments: [
          { label: "tools", to: "/tools" },
          { label: "content", to: { path: "/tools", query: { category: "content" } } },
        ],
        elevated: true,
      },
      global: {
        stubs: { RouterLink: routerLinkStub },
      },
    });

    const current = wrapper.get("[aria-current=page]");
    expect(current.element.tagName).toBe("A");
    expect(current.get("span").text()).toBe("content");
    expect(current.get("span").classes()).toContain("text-xl");
  });
});
