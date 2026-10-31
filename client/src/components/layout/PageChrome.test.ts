import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import PageChrome from "@/components/layout/PageChrome.vue";

const stubs = {
  BackLink: {
    props: ["to"],
    inheritAttrs: false,
    template:
      '<a :href="typeof to === \'string\' ? to : to.path" data-testid="back" v-bind="$attrs">back</a>',
  },
  PageBreadcrumbs: {
    props: ["segments", "elevated"],
    template:
      '<nav data-testid="crumbs"><span v-for="(s, i) in segments" :key="i" :data-elevated="elevated ? \'true\' : \'false\'" :data-to="s.to || \'\'">{{ s.label }}</span></nav>',
  },
  FieldHelp: {
    props: ["text", "size", "align", "placement", "interactive"],
    template:
      '<span data-testid="field-help" :data-text="text" :data-size="size" :data-align="align" :data-placement="placement" :data-interactive="interactive === false ? \'false\' : \'true\'">?</span>',
  },
};

describe("PageChrome", () => {
  it("shows parent + current crumbs elevated when last matches title (admin child)", () => {
    const wrapper = mount(PageChrome, {
      props: {
        title: "users",
        breadcrumbs: [{ label: "admin", to: "/admin" }, { label: "users" }],
        backTo: "/admin",
      },
      global: { stubs },
    });

    const crumbs = wrapper.findAll("[data-testid=crumbs] span");
    expect(crumbs).toHaveLength(2);
    expect(crumbs[0].text()).toBe("admin");
    expect(crumbs[0].attributes("data-to")).toBe("/admin");
    expect(crumbs[1].text()).toBe("users");
    expect(crumbs[1].attributes("data-elevated")).toBe("true");
    expect(wrapper.get("h1").classes()).toContain("sr-only");
    expect(wrapper.get("h1").text()).toBe("users");
    const back = wrapper.get("[data-testid=back]");
    expect(back.attributes("href")).toBe("/admin");
    // Back sits in the breadcrumb row (same vertical band) and parks on the nav rail.
    expect(back.element.parentElement?.className).toContain("my-[15px]");
    expect(back.element.parentElement?.className).toContain("min-h-10");
    expect(
      wrapper
        .findAll("div")
        .some((node) => node.classes().includes("h-10") && node.classes().includes("items-center")),
    ).toBe(true);
    expect(back.classes()).toContain("shell-outside-end");
    expect(back.classes()).toContain("!-right-6");
    expect(back.classes()).toContain("top-1/2");
  });

  it("shows tools parent + tool crumb for tools trails", () => {
    const wrapper = mount(PageChrome, {
      props: {
        title: "calculator",
        breadcrumbs: [{ label: "tools", to: "/tools" }, { label: "calculator" }],
        backTo: "/tools",
      },
      global: { stubs },
    });

    const crumbs = wrapper.findAll("[data-testid=crumbs] span");
    expect(crumbs.map((c) => c.text())).toEqual(["tools", "calculator"]);
    expect(crumbs[0].attributes("data-to")).toBe("/tools");
    expect(crumbs[1].attributes("data-elevated")).toBe("true");
    expect(wrapper.get("h1").classes()).toContain("sr-only");
    expect(wrapper.get("h1").text()).toBe("calculator");
  });

  it("keeps parent crumbs and sr-only h1 when last crumb does not match title (news article)", () => {
    const wrapper = mount(PageChrome, {
      props: {
        title: "Some Article",
        breadcrumbs: [{ label: "news", to: "/news" }, { label: "demo-news-1" }],
        backTo: "/news",
      },
      global: { stubs },
    });

    const crumbs = wrapper.findAll("[data-testid=crumbs] span");
    expect(crumbs.map((c) => c.text())).toEqual(["news", "demo-news-1"]);
    expect(crumbs[0].attributes("data-elevated")).toBe("true");
    expect(wrapper.get("h1").classes()).toContain("sr-only");
    expect(wrapper.get("h1").text()).toBe("Some Article");
    expect(wrapper.find(".accent-gradient").exists()).toBe(false);
  });

  it("omits the chrome h1 when the page renders its own heading", () => {
    const wrapper = mount(PageChrome, {
      props: {
        title: "Some Article",
        breadcrumbs: [{ label: "news", to: "/news" }, { label: "demo-news-1" }],
        backTo: "/news",
        omitHeading: true,
      },
      global: { stubs },
    });

    expect(wrapper.find("h1").exists()).toBe(false);
  });

  it("renders FieldHelp tip bottom-right when description is set", () => {
    const wrapper = mount(PageChrome, {
      props: {
        title: "db maintenance",
        breadcrumbs: [{ label: "admin", to: "/admin" }, { label: "db maintenance" }],
        backTo: "/admin",
        description: "backs up mongo, redis, and media.",
      },
      global: { stubs },
    });

    const pin = wrapper.get('[data-testid="page-chrome-help"]');
    expect(pin.classes()).toEqual(expect.arrayContaining(["absolute", "bottom-2", "right-0"]));
    const help = pin.get('[data-testid="field-help"]');
    expect(help.attributes("data-text")).toBe("backs up mongo, redis, and media.");
    expect(help.attributes("data-size")).toBe("sm");
    expect(help.attributes("data-align")).toBe("end");
    expect(help.attributes("data-placement")).toBe("top");
    expect(help.attributes("data-interactive")).toBe("true");
  });

  it("omits FieldHelp when description is unset", () => {
    const wrapper = mount(PageChrome, {
      props: {
        title: "admin",
        breadcrumbs: [{ label: "admin", to: "/admin" }],
      },
      global: { stubs },
    });

    expect(wrapper.find('[data-testid="page-chrome-help"]').exists()).toBe(false);
  });
});
