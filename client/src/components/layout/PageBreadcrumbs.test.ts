import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import PageBreadcrumbs from "@/components/layout/PageBreadcrumbs.vue";

describe("PageBreadcrumbs", () => {
  it("renders plain labels with muted ancestors and highlighted current", () => {
    const wrapper = mount(PageBreadcrumbs, {
      props: {
        segments: [{ label: "admin", to: "/admin" }, { label: "app logs" }],
        elevated: true,
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

    expect(wrapper.get("a").attributes("href")).toBe("/admin");
    expect(wrapper.get("a span").text()).toBe("admin");
    expect(wrapper.get("a span").classes()).toContain("text-surface-mid");
    expect(wrapper.get("a span").classes()).not.toContain("accent-gradient");

    const current = wrapper.get("[aria-current=page]");
    expect(current.text()).toBe("app logs");
    expect(current.classes()).toContain("accent-gradient");
    expect(current.classes()).toContain("text-lg");
    expect(wrapper.text()).toMatch(/admin\s*\/\s*app logs/);
  });

  it("applies elevated accent only on the current sole section crumb", () => {
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

    expect(wrapper.find("a").exists()).toBe(false);
    const current = wrapper.get("[aria-current=page]");
    expect(current.text()).toBe("admin");
    expect(current.classes()).toContain("accent-gradient");
    expect(current.classes()).toContain("text-lg");
  });

  it("highlights current without elevated title scale", () => {
    const wrapper = mount(PageBreadcrumbs, {
      props: {
        segments: [{ label: "tools", to: "/tools" }, { label: "calculator" }],
        elevated: false,
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

    const current = wrapper.get("[aria-current=page]");
    expect(current.text()).toBe("calculator");
    expect(current.classes()).toContain("font-medium");
    expect(current.classes()).toContain("text-surface-light");
    expect(current.classes()).not.toContain("accent-gradient");
  });
});
