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
    expect(button.text()).toContain("Save");
  });

  it("prepends a mapped action icon for semantic variants", () => {
    const wrapper = mount(BaseButton, {
      props: { variant: "create" },
      slots: { default: "recipe" },
    });
    expect(wrapper.find("svg").exists()).toBe(true);
    expect(wrapper.text()).toContain("recipe");
  });

  it("skips the mapped icon when icon is false", () => {
    const wrapper = mount(BaseButton, {
      props: { variant: "create", icon: false },
      slots: {
        default: '<span data-testid="custom-icon">x</span> recipe',
      },
    });
    expect(wrapper.find('[data-testid="custom-icon"]').exists()).toBe(true);
    expect(wrapper.findAll("svg")).toHaveLength(0);
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

    expect(button.classes()).toContain("hover:enabled:text-status-error/88");
    expect(button.classes()).toContain("hover:enabled:bg-status-error/12");
    expect(button.classes()).toContain("text-surface-light/60");
    expect(button.classes()).toContain("border-transparent");
  });

  it("colorizes success like pale primary wash", () => {
    const button = mount(BaseButton, {
      props: { variant: "success" },
    }).get("button");

    expect(button.classes()).toContain("bg-accent-coral/10");
    expect(button.classes()).toContain("text-accent-coral/88");
    expect(button.classes()).toContain("hover:enabled:bg-accent-coral/12");
    expect(button.classes()).toContain("active:enabled:bg-accent-coral/14");
    expect(button.classes()).toContain("focus-visible:ring-accent-coral/50");
  });

  it("colorizes primary as pale 1xx wash (matches cta-primary)", () => {
    const button = mount(BaseButton, {
      props: { variant: "primary" },
    }).get("button");

    expect(button.classes()).toContain("bg-accent-coral/10");
    expect(button.classes()).toContain("text-accent-coral/88");
    expect(button.classes()).toContain("hover:enabled:bg-accent-coral/12");
    expect(button.classes()).toContain("active:enabled:bg-accent-coral/14");
  });

  it("colorizes create like pale primary (1xx)", () => {
    const button = mount(BaseButton, {
      props: { variant: "create" },
    }).get("button");

    expect(button.classes()).toContain("bg-accent-coral/10");
    expect(button.classes()).toContain("text-accent-coral/88");
  });

  it("paints cancel as neutral ghost", () => {
    const button = mount(BaseButton, {
      props: { variant: "cancel" },
    }).get("button");

    expect(button.classes()).toContain("bg-transparent");
    expect(button.classes()).toContain("text-surface-light/80");
    expect(button.classes()).not.toContain("bg-status-critical/10");
    expect(button.classes()).toContain("focus-visible:ring-accent-coral/50");
  });

  it("paints edit as surface secondary", () => {
    const button = mount(BaseButton, {
      props: { variant: "edit" },
    }).get("button");

    expect(button.classes()).toContain("bg-surface-card");
    expect(button.classes()).toContain("border-surface-border");
    expect(button.classes()).not.toContain("bg-status-warning/10");
  });

  it("keeps secondary grayscale without accent wash", () => {
    const button = mount(BaseButton, {
      props: { variant: "secondary" },
    }).get("button");

    // Resting grayscale fill (NEUTRAL_SECONDARY_IDLE) — distinct from transparent ghost.
    expect(button.classes()).toContain("bg-surface-card");
    expect(button.classes()).toContain("border-surface-border");
    expect(button.classes()).toContain("text-surface-light/80");
    expect(button.classes()).toContain("hover:enabled:bg-surface-light/10");
    expect(button.classes()).not.toContain("bg-accent-coral/10");
    expect(button.classes()).not.toContain("text-accent-coral/88");
  });

  it("uses selected 1xx tint when primary selected", () => {
    const button = mount(BaseButton, {
      props: { variant: "primary", selected: true },
    }).get("button");

    expect(button.attributes("aria-pressed")).toBe("true");
    expect(button.classes()).toContain("bg-accent-coral/12");
    expect(button.classes()).toContain("text-accent-coral/88");
    expect(button.classes()).toContain("border-accent-coral/22");
  });
});
