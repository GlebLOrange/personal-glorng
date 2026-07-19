import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import PageBreadcrumbs from "@/components/layout/PageBreadcrumbs.vue";

describe("PageBreadcrumbs", () => {
  it("renders link segments with href", () => {
    const wrapper = mount(PageBreadcrumbs, {
      props: {
        segments: [
          { label: "tools", to: "/tools" },
          { label: "calculator" },
        ],
      },
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a :href="to"><slot /></a>',
          },
        },
      },
    });

    expect(wrapper.get("a").attributes("href")).toBe("/tools");
    expect(wrapper.text()).toContain("§ tools");
    expect(wrapper.text()).toContain("§ calculator");
  });

  it("applies elevated accent classes for sole section crumbs", () => {
    const wrapper = mount(PageBreadcrumbs, {
      props: {
        segments: [{ label: "admin", to: "/admin" }],
        elevated: true,
      },
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a :href="to" :class="$attrs.class"><slot /></a>',
          },
        },
      },
    });

    expect(wrapper.get("a").classes()).toContain("cursor-pointer");
    expect(wrapper.get("a span").classes()).toContain("accent-gradient");
    expect(wrapper.get("a span").classes()).toContain("text-lg");
    expect(wrapper.get("a span").text()).toBe("§ admin");
  });
});
