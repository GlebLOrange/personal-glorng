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
});
