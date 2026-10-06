import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import SiteLogo from "@/components/brand/SiteLogo.vue";

describe("SiteLogo", () => {
  it("renders the period-hinge mark as an aria-hidden svg", () => {
    const wrapper = mount(SiteLogo);

    const svg = wrapper.get("svg");
    expect(svg.attributes("aria-hidden")).toBe("true");
    expect(svg.attributes("viewBox")).toBe("0 0 64 64");
    expect(wrapper.findAll("path")).toHaveLength(2);
    expect(wrapper.get("circle").attributes("fill")).toBe("var(--color-accent-blue)");
  });
});
