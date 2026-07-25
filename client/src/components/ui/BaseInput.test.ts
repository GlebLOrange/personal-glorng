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

  it("keeps a faint full-width tip behind the value", async () => {
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
    expect(wrapper.get("input").attributes("aria-label")).toBe("enter title");
    expect(wrapper.find('button[aria-label="Clear"]').exists()).toBe(false);

    await wrapper.setProps({ modelValue: "Pasta Carbonara" });
    expect(wrapper.get("input").element).toHaveProperty("value", "Pasta Carbonara");
    expect(wrapper.get("#title-tip").text()).toBe("enter title");
    expect(wrapper.find('button[aria-label="Clear"]').exists()).toBe(true);
  });

  it("renders a suffix slot inside the shell and keeps the tip", () => {
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

    expect(wrapper.get("#ingredient-tip").text()).toBe("ingredient");
    expect(wrapper.get("input").element).toHaveProperty("value", "pasta");
    expect(wrapper.text()).toContain("↑");
    expect(wrapper.find('button[aria-label="Clear"]').exists()).toBe(true);
  });

  it("clears the shell value via the clear control", async () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "to",
        placeholder: "to",
        modelValue: "a@b.c",
        "onUpdate:modelValue": (value: string | number | null) =>
          wrapper.setProps({ modelValue: value }),
      },
    });

    await wrapper.get('button[aria-label="Clear"]').trigger("click");
    expect(wrapper.props("modelValue")).toBe("");
  });

  it("prefers placeholder help text as aria-label over the field label", () => {
    const wrapper = mount(BaseInput, {
      props: {
        id: "email",
        label: "Email",
        placeholder: "your@email.com",
      },
    });

    expect(wrapper.get("input").attributes("aria-label")).toBe("your@email.com");
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
