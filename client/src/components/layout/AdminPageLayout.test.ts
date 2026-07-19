import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";

const pageShellStub = {
  props: ["breadcrumbs", "backTo", "title"],
  template:
    '<div><span v-for="(seg, i) in breadcrumbs" :key="i" :data-to="seg.to || undefined">{{ seg.label }}</span></div>',
};

describe("AdminPageLayout", () => {
  it("renders admin / tool crumbs for admin hub pages", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "users" },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    const crumbs = wrapper.findAll("span");
    expect(crumbs.map((c) => c.text())).toEqual(["admin", "users"]);
    expect(crumbs[0].attributes("data-to")).toBe("/admin");
  });

  it("renders tools / tool crumbs when hub is tools", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "tasks", hub: "tools" },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    const crumbs = wrapper.findAll("span");
    expect(crumbs.map((c) => c.text())).toEqual(["tools", "tasks"]);
    expect(crumbs[0].attributes("data-to")).toBe("/tools");
  });

  it("uses a single admin crumb on the admin hub", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "admin", backTo: "/" },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    const crumbs = wrapper.findAll("span");
    expect(crumbs).toHaveLength(1);
    expect(crumbs[0].text()).toBe("admin");
    expect(crumbs[0].attributes("data-to")).toBe("/admin");
  });

  it("uses one-word users crumb under admin", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "users" },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    expect(wrapper.findAll("span").map((c) => c.text())).toEqual(["admin", "users"]);
  });

  it("keeps multi-word admin titles as a phrase crumb", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "app logs", hub: "tools" },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    expect(wrapper.findAll("span").map((c) => c.text())).toEqual(["tools", "app logs"]);
  });
});
