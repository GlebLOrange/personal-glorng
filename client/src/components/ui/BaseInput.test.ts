import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import BaseInput from "@/components/ui/BaseInput.vue";

describe("BaseInput", () => {
  it("associates the sr-only label with the input by default", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "email",
        label: "Email",
      },
    });

    expect(wrapper.get("label.sr-only").attributes("for")).toBe("email");
    expect(wrapper.get("input").attributes("id")).toBe("email");
    expect(wrapper.get("span.text-surface-sage").text()).toBe("Email");
  });

  it("renders a border-notch label when labelInside is false", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "email",
        label: "Email",
        labelInside: false,
      },
    });

    expect(wrapper.get("label:not(.sr-only)").attributes("for")).toBe("email");
    expect(wrapper.find("span.text-surface-sage").exists()).toBe(false);
  });

  it("wires error text via aria-describedby and aria-invalid", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "email",
        label: "Email",
        error: "Required",
      },
    });

    const input = wrapper.get("input");
    expect(input.attributes("aria-invalid")).toBe("true");
    expect(input.attributes("aria-describedby")).toBe("email-error");
    expect(wrapper.get("#email-error").attributes("role")).toBe("alert");
    expect(wrapper.get("#email-error").text()).toBe("Required");
  });

  it("shows overlay tip only when empty and reserves clear slot without jump", async () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "title",
        placeholder: "enter title",
        modelValue: "",
      },
    });

    expect(wrapper.find("label").exists()).toBe(false);
    expect(wrapper.get("input").attributes("placeholder")).toBeUndefined();
    expect(wrapper.get("#title-tip").text()).toBe("enter title");
    expect(wrapper.get("#title-tip").classes()).toContain("absolute");
    expect(wrapper.get("#title-tip").classes()).toContain("left-3");
    expect(wrapper.get("#title-tip").classes()).toContain("right-10");
    expect(wrapper.get("#title-tip").find(".truncate").classes()).toContain("text-left");
    expect(wrapper.get("#title-tip").attributes("aria-hidden")).toBe("true");
    expect(wrapper.get("input").attributes("aria-label")).toBeUndefined();
    expect(wrapper.find('button[aria-label="clear"]').exists()).toBe(false);
    expect(wrapper.find(".invisible.pointer-events-none").exists()).toBe(true);

    await wrapper.setProps({ modelValue: "Pasta Carbonara" });
    expect(wrapper.get("input").element).toHaveProperty("value", "Pasta Carbonara");
    expect(wrapper.find("#title-tip").exists()).toBe(false);
    const clearFilled = wrapper.get('button[aria-label="clear"]');
    expect(clearFilled.element.closest(".invisible")).toBeNull();
  });

  it("renders a suffix slot inside the shell and hides tip while typing", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "ingredient",
        placeholder: "ingredient",
        modelValue: "pasta",
      },
      attrs: {
        "aria-label": "ingredient 1",
      },
      slots: {
        suffix: '<button type="button">↑</button>',
      },
    });

    expect(wrapper.find("#ingredient-tip").exists()).toBe(false);
    expect(wrapper.get("input").element).toHaveProperty("value", "pasta");
    expect(wrapper.get("input").attributes("aria-label")).toBe("ingredient 1");
    expect(wrapper.text()).toContain("↑");
    expect(wrapper.get('button[aria-label="clear"]').element.closest(".invisible")).toBeNull();
  });

  it("clears the shell value and restores the tip without layout jump", async () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "to",
        placeholder: "to",
        modelValue: "a@b.c",
        "onUpdate:modelValue": (value: string | number | null) =>
          wrapper.setProps({ modelValue: value }),
      },
    });

    expect(wrapper.find("#to-tip").exists()).toBe(false);
    await wrapper.get('button[aria-label="clear"]').trigger("click");
    expect(wrapper.props("modelValue")).toBe("");
    expect(wrapper.get("#to-tip").text()).toBe("to");
    expect(wrapper.get("#to-tip").classes()).toContain("right-10");
    expect(wrapper.find('button[aria-label="clear"]').exists()).toBe(false);
  });

  it("shows inside label and suppresses placeholder tip when both are set", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "email",
        label: "Email",
        placeholder: "your@email.com",
      },
    });

    expect(wrapper.get("label.sr-only").attributes("for")).toBe("email");
    expect(wrapper.get("span.text-surface-sage").text()).toBe("Email");
    expect(wrapper.get("input").attributes("aria-label")).toBeUndefined();
    expect(wrapper.get("input").attributes("aria-describedby")).toBeUndefined();
    expect(wrapper.find("#email-tip").exists()).toBe(false);
  });

  it("does not put the visual tip into aria-describedby when hint is set", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "email",
        label: "Email",
        placeholder: "your@email.com",
        hint: "we never share this",
        labelInside: false,
      },
    });

    expect(wrapper.get("input").attributes("aria-describedby")).toBe("email-hint");
    expect(wrapper.get("#email-hint").text()).toBe("we never share this");
    expect(wrapper.get('button[aria-label="help"]').exists()).toBe(true);
    expect(wrapper.get("#email-tip").text()).toBe("your@email.com");
  });

  it("labelInside shows overlay while empty and suppresses tip + outer notch", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "pw",
        label: "password",
        placeholder: "password tip",
        modelValue: "",
      },
    });

    expect(wrapper.get("label.sr-only").attributes("for")).toBe("pw");
    expect(wrapper.get("label.sr-only").text()).toBe("password");
    // visual label mirrors tip overlay (absolute, behind value)
    expect(wrapper.get("span.text-surface-sage").text()).toBe("password");
    expect(wrapper.get("span.text-surface-sage").classes()).toContain("truncate");
    // tip suppressed when labelInside is active
    expect(wrapper.find("#pw-tip").exists()).toBe(false);
    expect(wrapper.find(".pt-2\\.5").exists()).toBe(false);
    expect(wrapper.get("input").attributes("aria-label")).toBeUndefined();
    expect(wrapper.find('button[aria-label="clear"]').exists()).toBe(false);
  });

  it("labelInside hides visual label and shows clear once typing", async () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "pw",
        label: "password",
        modelValue: "",
      },
    });

    expect(wrapper.find("span.text-surface-sage").exists()).toBe(true);
    await wrapper.setProps({ modelValue: "secret" });
    // visual label gone; sr-only stays for a11y
    expect(wrapper.find("span.text-surface-sage").exists()).toBe(false);
    expect(wrapper.find("label.sr-only").exists()).toBe(true);
    expect(wrapper.get('button[aria-label="clear"]').exists()).toBe(true);
  });

  it("labelInside still shows error in outer notch when error is present", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "pw",
        label: "password",
        error: "Required field",
      },
    });

    expect(wrapper.get("#pw-error").text()).toBe("Required field");
    expect(wrapper.get("input").attributes("aria-invalid")).toBe("true");
    // outer notch position is reserved for the error
    expect(wrapper.find(".pt-2\\.5").exists()).toBe(true);
  });

  it("applies success and error border tones", () => {
    const success = mount(BaseInput, {
      props: { id: "ok", label: "Email", tone: "success" },
    });
    expect(success.get("div.ring-status-success").exists()).toBe(true);

    const bad = mount(BaseInput, {
      props: { id: "bad", label: "Email", tone: "error" },
    });
    expect(bad.get("div.ring-status-error").exists()).toBe(true);
    expect(bad.get("input").attributes("aria-invalid")).toBe("true");
  });
});
