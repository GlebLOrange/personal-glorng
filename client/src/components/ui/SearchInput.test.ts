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

    const clear = wrapper.get('button[aria-label="Clear search"]');
    expect(clear.classes().join(" ")).not.toMatch(/invisible/);
    expect(clear.element.closest(".invisible")).toBeNull();
    await clear.trigger("click");
    expect(wrapper.props("modelValue")).toBe("");
  });

  it("reserves the clear slot when empty but keeps the X invisible", () => {
    const wrapper = mount(SearchInput, {
      props: { modelValue: "", placeholder: "search" },
    });
    expect(wrapper.find('button[aria-label="Clear search"]').exists()).toBe(false);
    expect(wrapper.find(".invisible.pointer-events-none").exists()).toBe(true);
  });

  it("shows the overlay label only when empty", async () => {
    const wrapper = mount(SearchInput, {
      props: {
        id: "recipes-search",
        modelValue: "",
        placeholder: "search recipes",
      },
    });

    expect(wrapper.get("#recipes-search-overlay").text()).toBe("search recipes");
    expect(wrapper.get("#recipes-search-overlay").attributes("aria-hidden")).toBe("true");
    expect(wrapper.get("input").attributes("placeholder")).toBeUndefined();

    await wrapper.setProps({ modelValue: "pasta" });
    expect(wrapper.find("#recipes-search-overlay").exists()).toBe(false);
  });

  it("hides the overlay when a space is typed", async () => {
    const wrapper = mount(SearchInput, {
      props: {
        id: "space-search",
        modelValue: "",
        placeholder: "search",
      },
    });
    expect(wrapper.find("#space-search-overlay").exists()).toBe(true);
    await wrapper.setProps({ modelValue: " " });
    expect(wrapper.find("#space-search-overlay").exists()).toBe(false);
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
