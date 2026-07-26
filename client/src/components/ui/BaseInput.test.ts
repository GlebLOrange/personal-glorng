import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import BaseInput from "@/components/ui/BaseInput.vue";

describe("BaseInput", () => {
  it("associates the visible label with the input", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "email",
        label: "Email",
      },
    });

    expect(wrapper.get("label").attributes("for")).toBe("email");
    expect(wrapper.get("input").attributes("id")).toBe("email");
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
    expect(wrapper.get("#title-tip").classes()).toContain("right-11");
    expect(wrapper.get("#title-tip").find(".truncate").classes()).toContain("text-right");
    expect(wrapper.get("#title-tip").attributes("aria-hidden")).toBe("true");
    expect(wrapper.get("input").attributes("aria-label")).toBeUndefined();
    const clearEmpty = wrapper.get('button[aria-label="Clear"]');
    expect(clearEmpty.element.closest(".invisible")).not.toBeNull();

    await wrapper.setProps({ modelValue: "Pasta Carbonara" });
    expect(wrapper.get("input").element).toHaveProperty("value", "Pasta Carbonara");
    expect(wrapper.find("#title-tip").exists()).toBe(false);
    const clearFilled = wrapper.get('button[aria-label="Clear"]');
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
    expect(wrapper.get('button[aria-label="Clear"]').element.closest(".invisible")).toBeNull();
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
    await wrapper.get('button[aria-label="Clear"]').trigger("click");
    expect(wrapper.props("modelValue")).toBe("");
    expect(wrapper.get("#to-tip").text()).toBe("to");
    expect(wrapper.get("#to-tip").classes()).toContain("right-11");
    expect(wrapper.get('button[aria-label="Clear"]').element.closest(".invisible")).not.toBeNull();
  });

  it("uses a visible label for naming when label and placeholder are both set", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "email",
        label: "Email",
        placeholder: "your@email.com",
      },
    });

    expect(wrapper.get("label").attributes("for")).toBe("email");
    expect(wrapper.get("label").text()).toBe("Email");
    expect(wrapper.get("input").attributes("aria-label")).toBeUndefined();
    expect(wrapper.get("input").attributes("aria-describedby")).toBeUndefined();
    expect(wrapper.get("#email-tip").text()).toBe("your@email.com");
    expect(wrapper.get("#email-tip").attributes("aria-hidden")).toBe("true");
  });

  it("does not put the visual tip into aria-describedby when hint is set", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "email",
        label: "Email",
        placeholder: "your@email.com",
        hint: "We never share this",
      },
    });

    expect(wrapper.get("input").attributes("aria-describedby")).toBe("email-hint");
    expect(wrapper.get("#email-tip").text()).toBe("your@email.com");
  });

  it("applies success and error border tones", () => {
    const success = mount(BaseInput, {
      props: { id: "ok", label: "Email", tone: "success" },
    });
    expect(success.get("input").classes()).toContain("border-status-success");

    const bad = mount(BaseInput, {
      props: { id: "bad", label: "Email", tone: "error" },
    });
    expect(bad.get("input").classes()).toContain("border-status-error");
    expect(bad.get("input").attributes("aria-invalid")).toBe("true");
  });
});
