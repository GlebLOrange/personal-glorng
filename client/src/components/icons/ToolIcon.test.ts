import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ToolIcon from "@/components/icons/ToolIcon.vue";
import { PLATFORM_SERVICES } from "@/platform/services";

const HUB_SLUGS = ["users", "sync", "location", "tools", "admin", "settings"] as const;

describe("ToolIcon", () => {
  it.each(PLATFORM_SERVICES.map((s) => s.slug))(
    "renders a dedicated svg for catalog slug %s",
    (slug) => {
      const wrapper = mount(ToolIcon, { props: { slug } });
      expect(wrapper.find("svg").exists()).toBe(true);
      expect(wrapper.find("svg").attributes("aria-hidden")).toBe("true");
      expect(wrapper.find('[data-icon="fallback"]').exists()).toBe(false);
    },
  );

  it.each(HUB_SLUGS)("renders an svg for hub slug %s", (slug) => {
    const wrapper = mount(ToolIcon, { props: { slug } });
    expect(wrapper.find("svg").exists()).toBe(true);
    expect(wrapper.find("svg").attributes("aria-hidden")).toBe("true");
    expect(wrapper.find('[data-icon="fallback"]').exists()).toBe(false);
  });

  it("uses the fallback square for unknown slugs", () => {
    const wrapper = mount(ToolIcon, { props: { slug: "unknown-fallback" } });
    expect(wrapper.find('[data-icon="fallback"]').exists()).toBe(true);
  });

  it("renders admin as four spaced dashboard panels", () => {
    const wrapper = mount(ToolIcon, { props: { slug: "admin" } });
    const rects = wrapper.findAll("rect");
    expect(rects).toHaveLength(4);
    expect(rects.map((r) => r.attributes("x")).sort()).toEqual(["14", "14", "3", "3"]);
    expect(rects.some((r) => r.attributes("x") === "4")).toBe(false);
    expect(rects.some((r) => r.attributes("x") === "13")).toBe(false);
  });

  it("renders qr-generator with spaced finders and filled modules", () => {
    const wrapper = mount(ToolIcon, { props: { slug: "qr-generator" } });
    const stroked = wrapper
      .findAll("rect")
      .filter((r) => r.attributes("stroke") !== "none");
    const filled = wrapper
      .findAll("rect")
      .filter((r) => r.attributes("fill") === "currentColor");
    expect(stroked).toHaveLength(3);
    expect(filled).toHaveLength(4);
    expect(stroked.some((r) => r.attributes("x") === "4")).toBe(false);
    expect(stroked.some((r) => r.attributes("x") === "13")).toBe(false);
  });
});
