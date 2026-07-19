import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import BaseButton from "@/components/ui/BaseButton.vue";

describe("BaseButton", () => {
  it("sets aria-busy and disables while loading", () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true },
      slots: { default: "Save" },
    });

    const button = wrapper.get("button");
    expect(button.attributes("aria-busy")).toBe("true");
    expect(button.attributes("disabled")).toBeDefined();
    expect(button.text()).toBe("Save");
  });

  it("keeps sm/md/field at input height; lg is taller", () => {
    expect(mount(BaseButton, { props: { size: "sm" } }).get("button").classes()).toContain("h-11");
    expect(mount(BaseButton, { props: { size: "md" } }).get("button").classes()).toContain("h-11");
    expect(mount(BaseButton, { props: { size: "field" } }).get("button").classes()).toContain(
      "h-11",
    );
    expect(mount(BaseButton, { props: { size: "lg" } }).get("button").classes()).toContain("h-12");
  });

  it("applies red hover styles when danger", () => {
    const button = mount(BaseButton, {
      props: { variant: "ghost", danger: true },
    }).get("button");

    expect(button.classes()).toContain("hover:enabled:text-status-error");
    expect(button.classes()).toContain("hover:enabled:border-status-error");
  });
});
