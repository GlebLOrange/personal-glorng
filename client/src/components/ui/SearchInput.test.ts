import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import SearchInput from "@/components/ui/SearchInput.vue";

describe("SearchInput", () => {
  it("shows a clear control when there is a value and clears on click", async () => {
    const wrapper = mount(SearchInput, {
      props: {
        modelValue: "pasta",
        placeholder: "search",
        "onUpdate:modelValue": (value: string) => wrapper.setProps({ modelValue: value }),
      },
    });

    expect(wrapper.find('button[aria-label="Clear search"]').exists()).toBe(true);
    await wrapper.get('button[aria-label="Clear search"]').trigger("click");
    expect(wrapper.props("modelValue")).toBe("");
  });

  it("hides the clear control when empty", () => {
    const wrapper = mount(SearchInput, {
      props: { modelValue: "", placeholder: "search" },
    });
    expect(wrapper.find('button[aria-label="Clear search"]').exists()).toBe(false);
  });

  it("names the field Search by default, not the decorative placeholder", () => {
    const wrapper = mount(SearchInput, {
      props: { modelValue: "", placeholder: "search recipes" },
    });
    expect(wrapper.get("input").attributes("aria-label")).toBe("Search");
  });

  it("uses ariaLabel when provided", () => {
    const wrapper = mount(SearchInput, {
      props: { modelValue: "", placeholder: "search", ariaLabel: "Find recipes" },
    });
    expect(wrapper.get("input").attributes("aria-label")).toBe("Find recipes");
  });
});
