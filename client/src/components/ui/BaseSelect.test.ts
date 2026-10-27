import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import BaseSelect from "@/components/ui/BaseSelect.vue";

const options = {
  default: '<option value="en">English</option>',
};

describe("BaseSelect", () => {
  it("omits hint chrome and aria wiring when no hint is provided", () => {
    const wrapper = mount(BaseSelect, {
      props: { id: "language", label: "Language" },
      slots: options,
    });

    expect(wrapper.get("select").attributes("id")).toBe("language");
    expect(wrapper.get("select").attributes("aria-describedby")).toBeUndefined();
    expect(wrapper.find('button[aria-label="help"]').exists()).toBe(false);
    expect(wrapper.get("label.sr-only").text()).toBe("Language");
  });

  it("renders the hint popover and describedby when a hint is provided", () => {
    const wrapper = mount(BaseSelect, {
      props: {
        id: "language",
        label: "Language",
        labelAlign: "start",
        hint: "used for article language",
      },
      slots: options,
    });

    const select = wrapper.get("select");
    expect(select.attributes("aria-describedby")).toBe("language-hint");
    expect(wrapper.get("#language-hint").text()).toBe("used for article language");
    expect(wrapper.get('button[aria-label="help"]').exists()).toBe(true);
    expect(wrapper.get("label:not(.sr-only)").text()).toBe("Language");
  });

  it("keeps the help affordance in the inline-end layout without a border notch", () => {
    const wrapper = mount(BaseSelect, {
      props: { id: "language", hint: "used for article language" },
      slots: options,
    });

    expect(wrapper.get("select").attributes("aria-describedby")).toBe("language-hint");
    expect(wrapper.get('button[aria-label="help"]').exists()).toBe(true);
    expect(wrapper.find("label:not(.sr-only)").exists()).toBe(false);
  });
});
