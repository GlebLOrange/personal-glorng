import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import PageShell from "@/components/layout/PageShell.vue";

const stubs = {
  PageChrome: {
    props: ["description", "backTo"],
    template: `<div data-testid="chrome" :data-description="description ?? ''" :data-back="backTo ?? ''" />`,
  },
  PinnedToolsRow: { template: '<div data-testid="pinned" />' },
  BackLink: { props: ["to"], template: '<a data-testid="back" :href="to" aria-label="back" />' },
};

describe("PageShell", () => {
  it("forwards backTo to PageChrome (Back lives in the breadcrumb row)", () => {
    const wrapper = mount(PageShell, {
      props: { title: "users", breadcrumbs: [{ label: "users" }], backTo: "/admin" },
      global: { stubs },
      slots: { default: "<div>body</div>" },
    });
    expect(wrapper.get('[data-testid="chrome"]').attributes("data-back")).toBe("/admin");
    expect(wrapper.find('[data-testid="back"]').exists()).toBe(false);
  });

  it("leaves chrome Back unset when backTo is unset", () => {
    const wrapper = mount(PageShell, {
      props: { title: "tools", breadcrumbs: [{ label: "tools" }] },
      global: { stubs },
      slots: { default: "<div>body</div>" },
    });
    expect(wrapper.get('[data-testid="chrome"]').attributes("data-back")).toBe("");
  });

  it("forwards description to PageChrome when set", () => {
    const wrapper = mount(PageShell, {
      props: {
        title: "news",
        breadcrumbs: [{ label: "news" }],
        description: "Curated digest from scheduled RSS ingest.",
      },
      global: { stubs },
      slots: { default: "<div>body</div>" },
    });

    expect(wrapper.get('[data-testid="chrome"]').attributes("data-description")).toBe(
      "Curated digest from scheduled RSS ingest.",
    );
    expect(wrapper.find('[data-testid="page-description"]').exists()).toBe(false);
  });

  it("omits chrome description when unset", () => {
    const wrapper = mount(PageShell, {
      props: {
        title: "tools",
        breadcrumbs: [{ label: "tools" }],
      },
      global: { stubs },
      slots: { default: "<div>body</div>" },
    });

    expect(wrapper.get('[data-testid="chrome"]').attributes("data-description")).toBe("");
  });

  it("wraps the slot in page-tool-body when tool is true", () => {
    const wrapper = mount(PageShell, {
      props: {
        title: "send email",
        breadcrumbs: [{ label: "tools", to: "/tools" }, { label: "send email" }],
        tool: true,
      },
      global: { stubs },
      slots: { default: '<div data-testid="slot-body">body</div>' },
    });

    expect(wrapper.find(".page-tool-body").exists()).toBe(true);
    expect(wrapper.get(".page-tool-body").get('[data-testid="slot-body"]').text()).toBe("body");
  });

  it("wraps the slot in page-tool-body when bodyWidth is column", () => {
    const wrapper = mount(PageShell, {
      props: {
        title: "settings",
        breadcrumbs: [{ label: "settings" }],
        bodyWidth: "column",
      },
      global: { stubs },
      slots: { default: '<div data-testid="slot-body">body</div>' },
    });

    expect(wrapper.find(".page-tool-body").exists()).toBe(true);
    expect(wrapper.get(".page-tool-body").get('[data-testid="slot-body"]').text()).toBe("body");
  });

  it("does not wrap the slot in page-tool-body by default", () => {
    const wrapper = mount(PageShell, {
      props: {
        title: "news",
        breadcrumbs: [{ label: "news" }],
      },
      global: { stubs },
      slots: { default: '<div data-testid="slot-body">body</div>' },
    });

    expect(wrapper.find(".page-tool-body").exists()).toBe(false);
    expect(wrapper.get('[data-testid="slot-body"]').text()).toBe("body");
  });

  it("renders the footer slot last inside page-body, after page-tool-body", () => {
    const wrapper = mount(PageShell, {
      props: { title: "recipes", breadcrumbs: [{ label: "recipes" }], bodyWidth: "column" },
      global: { stubs },
      slots: {
        default: '<div data-testid="slot-body">body</div>',
        footer: '<nav data-testid="pager">pager</nav>',
      },
    });

    const body = wrapper.get(".page-body").element;
    const footer = body.lastElementChild as HTMLElement;
    expect(footer.classList.contains("page-body-footer")).toBe(true);
    expect(footer.querySelector('[data-testid="pager"]')).not.toBeNull();
    expect(wrapper.get(".page-tool-body").find('[data-testid="pager"]').exists()).toBe(false);
  });

  it("omits the footer wrapper without a footer slot", () => {
    const wrapper = mount(PageShell, {
      props: { title: "news", breadcrumbs: [{ label: "news" }] },
      global: { stubs },
      slots: { default: "<div>body</div>" },
    });

    expect(wrapper.find(".page-body-footer").exists()).toBe(false);
  });
});
