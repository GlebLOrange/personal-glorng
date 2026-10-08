import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import SiteLogo from "@/components/brand/SiteLogo.vue";

describe("SiteLogo", () => {
  it("renders the mark asset as an aria-hidden img", () => {
    const wrapper = mount(SiteLogo);

    const img = wrapper.get("img");
    expect(img.attributes("aria-hidden")).toBe("true");
    expect(img.attributes("src")).toBe("/brand/gy-mark-simple.svg");
    expect(img.attributes("alt")).toBe("");
  });

  it("uses the full logo asset when variant is full", () => {
    const wrapper = mount(SiteLogo, { props: { variant: "full" } });

    expect(wrapper.get("img").attributes("src")).toBe("/brand/gy-logo.svg");
  });
});
