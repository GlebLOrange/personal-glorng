import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import AdminBreadcrumbs from "@/components/layout/AdminBreadcrumbs.vue";

describe("AdminBreadcrumbs", () => {
  it("links the tools crumb to the authenticated dashboard", () => {
    const wrapper = mount(AdminBreadcrumbs, {
      props: { currentLabel: "tasks" },
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
  });
});
