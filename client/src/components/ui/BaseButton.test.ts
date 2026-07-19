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
});
