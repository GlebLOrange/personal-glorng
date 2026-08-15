import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { describe, expect, it, vi } from "vitest";

import PasswordGeneratorTool from "@/pages/tools/PasswordGeneratorTool.vue";

vi.mock("@/composables/useApi", () => ({
  api: {
    post: vi.fn().mockResolvedValue({ data: { password: "generated_test_pass_123!" } }),
  },
}));

describe("PasswordGeneratorTool", () => {
  it("renders with options dropdown first, then length input, then generate button and reset button", () => {
    const wrapper = mount(PasswordGeneratorTool, {
      global: {
        stubs: {
          PageShell: { template: "<div><slot /></div>" },
        },
      },
    });

    const form = wrapper.find("form");
    expect(form.exists()).toBe(true);

    const filterDropdown = wrapper.findComponent({ name: "AdminFilterDropdown" });
    const baseInput = wrapper.findComponent({ name: "BaseInput" });
    const iconActionButton = wrapper.findComponent({ name: "IconActionButton" });

    expect(filterDropdown.exists()).toBe(true);
    expect(baseInput.exists()).toBe(true);
    expect(iconActionButton.exists()).toBe(true);
  });

  it("resets options and forgets generated password when reset button is clicked", async () => {
    const wrapper = mount(PasswordGeneratorTool, {
      global: {
        stubs: {
          PageShell: { template: "<div><slot /></div>" },
        },
      },
    });

    const form = wrapper.find("form");
    await form.trigger("submit");
    await nextTick();
    await vi.waitFor(() =>
      expect(wrapper.findAllComponents({ name: "BaseInput" })).toHaveLength(2),
    );

    const resetButton = wrapper.findComponent({ name: "IconActionButton" });
    await resetButton.trigger("click");
    await nextTick();

    expect(wrapper.findAllComponents({ name: "BaseInput" })).toHaveLength(1);
  });
});
