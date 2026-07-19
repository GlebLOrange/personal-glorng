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

    await wrapper.setProps({ modelValue: "Pasta Carbonara" });
    expect(wrapper.get("input").element).toHaveProperty("value", "Pasta Carbonara");
    expect(wrapper.get("#title-tip").text()).toBe("enter title");
  });

  it("renders a suffix slot inside the shell and hides the tip", () => {
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
    expect(wrapper.text()).toContain("↑");
  });
});
