import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";

const pageShellStub = {
  props: ["breadcrumbs", "backTo", "title", "description"],
  template:
    '<div><span data-testid="description">{{ description || "" }}</span><span v-for="(seg, i) in breadcrumbs" :key="i" data-testid="crumb" :data-to="seg.to || undefined">{{ seg.label }}</span></div>',
};

function crumbNodes(wrapper: ReturnType<typeof mount>) {
  return wrapper.findAll('[data-testid="crumb"]');
}

describe("AdminPageLayout", () => {
  it("renders tools / tool crumbs by default", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "users" },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    const crumbs = crumbNodes(wrapper);
    expect(crumbs.map((c) => c.text())).toEqual(["tools", "users"]);
    expect(crumbs[0].attributes("data-to")).toBe("/tools");
  });

  it("renders tools / tool crumbs when hub is tools", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "tasks", hub: "tools" },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    const crumbs = crumbNodes(wrapper);
    expect(crumbs.map((c) => c.text())).toEqual(["tools", "tasks"]);
    expect(crumbs[0].attributes("data-to")).toBe("/tools");
  });

  it("nests the admin page under tools when hub is tools", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "admin", hub: "tools", backTo: "/tools" },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    const crumbs = crumbNodes(wrapper);
    expect(crumbs.map((c) => c.text())).toEqual(["tools", "admin"]);
    expect(crumbs[0].attributes("data-to")).toBe("/tools");
  });

  it("uses one-word users crumb under tools", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "users" },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    expect(crumbNodes(wrapper).map((c) => c.text())).toEqual(["tools", "users"]);
  });

  it("keeps multi-word admin titles as a phrase crumb", () => {
    const wrapper = mount(AdminPageLayout, {
      props: { title: "app logs", hub: "tools" },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    expect(crumbNodes(wrapper).map((c) => c.text())).toEqual(["tools", "app logs"]);
  });

  it("forwards description to PageShell", () => {
    const wrapper = mount(AdminPageLayout, {
      props: {
        title: "health checker",
        description: "Monitor URLs on a schedule — status history stays on this server.",
      },
      global: { stubs: { PageShell: pageShellStub } },
      slots: { default: "content" },
    });

    expect(wrapper.get('[data-testid="description"]').text()).toBe(
      "Monitor URLs on a schedule — status history stays on this server.",
    );
  });
});
