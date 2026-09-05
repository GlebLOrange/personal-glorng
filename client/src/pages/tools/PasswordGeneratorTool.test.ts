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
    const lengthInput = wrapper.findAllComponents({ name: "BaseInput" })[0];
    const iconActionButton = wrapper.findComponent({ name: "IconActionButton" });

    expect(filterDropdown.exists()).toBe(true);
    expect(lengthInput?.exists()).toBe(true);
    expect(iconActionButton.exists()).toBe(true);
    expect(lengthInput?.props("label")).toBe("length");
    expect(
      filterDropdown.element.compareDocumentPosition(lengthInput!.element) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
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

  it("forgets generated password on field clear without resetting options", async () => {
    const wrapper = mount(PasswordGeneratorTool, {
      global: {
        stubs: {
          PageShell: { template: "<div><slot /></div>" },
        },
      },
      attachTo: document.body,
    });

    const form = wrapper.find("form");
    await form.trigger("submit");
    await nextTick();
    await vi.waitFor(() =>
      expect(wrapper.findAllComponents({ name: "BaseInput" })).toHaveLength(2),
    );

    const filterTrigger = wrapper.get('button[aria-haspopup="dialog"]');
    await filterTrigger.trigger("click");
    await nextTick();

    const uppercaseChip = wrapper
      .findAll("button[aria-pressed]")
      .find((btn) => btn.text().trim() === "uppercase");
    expect(uppercaseChip).toBeTruthy();
    await uppercaseChip!.trigger("click");
    await nextTick();
    expect(uppercaseChip!.attributes("aria-pressed")).toBe("false");

    const clearButton = wrapper.get('button[aria-label="clear"]');
    await clearButton.trigger("click");
    await nextTick();

    expect(wrapper.findAllComponents({ name: "BaseInput" })).toHaveLength(1);

    await filterTrigger.trigger("click");
    await nextTick();
    const uppercaseAfter = wrapper
      .findAll("button[aria-pressed]")
      .find((btn) => btn.text().trim() === "uppercase");
    expect(uppercaseAfter?.attributes("aria-pressed")).toBe("false");

    wrapper.unmount();
  });
});
