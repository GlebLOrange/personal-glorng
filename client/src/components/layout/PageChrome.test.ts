import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import PageChrome from "@/components/layout/PageChrome.vue";

const stubs = {
  BackLink: {
    props: ["to"],
    template: '<a :href="typeof to === \'string\' ? to : to.path" data-testid="back">back</a>',
  },
  PageBreadcrumbs: {
    props: ["segments", "elevated"],
    template:
      '<nav data-testid="crumbs"><span v-for="(s, i) in segments" :key="i" :data-elevated="elevated ? \'true\' : \'false\'">{{ s.label }}</span></nav>',
  },
};

describe("PageChrome", () => {
  it("shows only the last crumb elevated when it matches the title (admin child)", () => {
    const wrapper = mount(PageChrome, {
      props: {
        title: "users",
        breadcrumbs: [
          { label: "admin", to: "/admin" },
          { label: "users" },
        ],
        backTo: "/admin",
      },
      global: { stubs },
    });

    const crumbs = wrapper.findAll("[data-testid=crumbs] span");
    expect(crumbs).toHaveLength(1);
    expect(crumbs[0].text()).toBe("users");
    expect(crumbs[0].attributes("data-elevated")).toBe("true");
    expect(wrapper.find("h1").exists()).toBe(false);
    expect(wrapper.get("[data-testid=back]").attributes("href")).toBe("/admin");
  });

  it("shows only the tool crumb for tools trails", () => {
    const wrapper = mount(PageChrome, {
      props: {
        title: "calculator",
        breadcrumbs: [
          { label: "tools", to: "/tools" },
          { label: "calculator" },
        ],
        backTo: "/tools",
      },
      global: { stubs },
    });

    const crumbs = wrapper.findAll("[data-testid=crumbs] span");
    expect(crumbs.map((c) => c.text())).toEqual(["calculator"]);
    expect(crumbs[0].attributes("data-elevated")).toBe("true");
    expect(wrapper.find("h1").exists()).toBe(false);
  });

  it("keeps parent crumb + h1 when last crumb does not match title (news article)", () => {
    const wrapper = mount(PageChrome, {
      props: {
        title: "Some Article",
        breadcrumbs: [{ label: "news", to: "/news" }],
        backTo: "/news",
      },
      global: { stubs },
    });

    const crumbs = wrapper.findAll("[data-testid=crumbs] span");
    expect(crumbs.map((c) => c.text())).toEqual(["news"]);
    expect(crumbs[0].attributes("data-elevated")).toBe("true");
    expect(wrapper.get("h1").text()).toContain("Some...");
    expect(wrapper.get("h1").attributes("title")).toBe("Some Article");
  });
});
