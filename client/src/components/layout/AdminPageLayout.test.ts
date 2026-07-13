import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";

describe("AdminPageLayout", () => {
  it("renders admin tools breadcrumb linking to /admin", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "tasks" },
      global: {
        stubs: {
          PageShell: {
            props: ["breadcrumbs"],
            template: '<div><a v-for="(seg, i) in breadcrumbs" :key="i" :href="seg.to">{{ seg.label }}</a></div>',
          },
        },
      },
      slots: { default: "content" },
    });

    expect(wrapper.get("a").attributes("href")).toBe("/admin");
    expect(wrapper.text()).toContain("tools");
    expect(wrapper.text()).toContain("tasks");
  });
});
