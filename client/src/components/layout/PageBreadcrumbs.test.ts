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
    expect(wrapper.text()).toContain("calculator");
  });
});
