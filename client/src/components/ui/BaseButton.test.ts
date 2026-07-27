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

  it("keeps sm/md/field at input height; lg is taller; icon is square h-11", () => {
    expect(
      mount(BaseButton, { props: { size: "sm" } })
        .get("button")
        .classes(),
    ).toContain("h-11");
    expect(
      mount(BaseButton, { props: { size: "md" } })
        .get("button")
        .classes(),
    ).toContain("h-11");
    expect(
      mount(BaseButton, { props: { size: "field" } })
        .get("button")
        .classes(),
    ).toContain("h-11");
    expect(
      mount(BaseButton, { props: { size: "lg" } })
        .get("button")
        .classes(),
    ).toContain("h-12");
    const icon = mount(BaseButton, { props: { size: "icon" } }).get("button");
    expect(icon.classes()).toContain("h-11");
    expect(icon.classes()).toContain("w-11");
    expect(icon.classes()).toContain("min-w-11");
    expect(icon.classes()).toContain("px-0");
  });

  it("applies muted quiet danger styles on ghost danger", () => {
    const button = mount(BaseButton, {
      props: { variant: "ghost", danger: true },
    }).get("button");

    expect(button.classes()).toContain("hover:enabled:text-status-error");
    expect(button.classes()).toContain("hover:enabled:bg-status-error/15");
    expect(button.classes()).toContain("text-surface-light/60");
    expect(button.classes()).toContain("border-transparent");
  });

  it("colorizes success with fill/3 matching accent text and pale hover", () => {
    const button = mount(BaseButton, {
      props: { variant: "success" },
    }).get("button");

    expect(button.classes()).toContain("bg-status-success/3");
    expect(button.classes()).toContain("text-status-success");
    expect(button.classes()).toContain("hover:enabled:bg-status-success/15");
    expect(button.classes()).toContain("active:enabled:bg-status-success/25");
    expect(button.classes()).toContain("focus-visible:ring-status-success/50");
  });

  it("colorizes primary with fill/3 matching accent text and pale hover", () => {
    const button = mount(BaseButton, {
      props: { variant: "primary" },
    }).get("button");

    expect(button.classes()).toContain("bg-accent-blue/3");
    expect(button.classes()).toContain("text-accent-blue");
    expect(button.classes()).toContain("hover:enabled:bg-accent-blue/15");
    expect(button.classes()).toContain("active:enabled:bg-accent-blue/25");
  });

  it("keeps secondary grayscale without accent wash", () => {
    const button = mount(BaseButton, {
      props: { variant: "secondary" },
    }).get("button");

    expect(button.classes()).toContain("bg-transparent");
    expect(button.classes()).toContain("text-surface-light/80");
    expect(button.classes()).toContain("hover:enabled:bg-surface-light/10");
    expect(button.classes()).not.toContain("bg-accent-blue/3");
    expect(button.classes()).not.toContain("text-accent-blue");
    expect(button.classes()).toContain("border-transparent");
  });

  it("persists pale tint when selected", () => {
    const button = mount(BaseButton, {
      props: { variant: "primary", selected: true },
    }).get("button");

    expect(button.attributes("aria-pressed")).toBe("true");
    expect(button.classes()).toContain("bg-accent-blue/15");
    expect(button.classes()).toContain("text-accent-blue");
  });
});
