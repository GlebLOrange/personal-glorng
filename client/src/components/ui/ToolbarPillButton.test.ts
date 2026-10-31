import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";

describe("ToolbarPillButton", () => {
  it("prepends a mapped action icon", () => {
    const wrapper = mount(ToolbarPillButton, {
      props: { action: "create" },
      slots: { default: "recipe" },
    });
    expect(wrapper.find("svg").exists()).toBe(true);
    expect(wrapper.text()).toContain("recipe");
  });

  it("skips the mapped icon when icon is false", () => {
    const wrapper = mount(ToolbarPillButton, {
      props: { action: "create", icon: false },
      slots: {
        default: '<span data-testid="custom-icon">x</span> recipe',
      },
    });
    expect(wrapper.find('[data-testid="custom-icon"]').exists()).toBe(true);
    expect(wrapper.findAll("svg")).toHaveLength(0);
  });
});
