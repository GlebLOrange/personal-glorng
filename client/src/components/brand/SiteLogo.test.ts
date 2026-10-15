import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it } from "vitest";

import SiteLogo from "@/components/brand/SiteLogo.vue";
import { colorThemeResolved } from "@/composables/useColorTheme";

describe("SiteLogo", () => {
  beforeEach(() => {
    colorThemeResolved.value = "dark";
  });

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

  it("uses light mark and lockup assets when theme is light", async () => {
    colorThemeResolved.value = "light";
    const mark = mount(SiteLogo);
    expect(mark.get("img").attributes("src")).toBe("/brand/gy-mark-simple-light.svg");

    const full = mount(SiteLogo, { props: { variant: "full" } });
    expect(full.get("img").attributes("src")).toBe("/brand/gy-logo-light.svg");
  });
});
