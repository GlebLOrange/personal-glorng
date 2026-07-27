import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { describe, expect, it } from "vitest";

import DataExtractOptionsPanel from "@/components/admin/data-extract/DataExtractOptionsPanel.vue";

describe("DataExtractOptionsPanel popover a11y", () => {
  it("focuses the first control on open, closes on Escape, and restores trigger focus", async () => {
    const wrapper = mount(DataExtractOptionsPanel, {
      props: {
        formatChoice: "auto",
        profileChoice: "custom",
        fieldDelimiter: "|",
        listDelimiter: ";",
        rowTag: "",
        xmlMode: "rows",
        hasCustomOptions: false,
        showDelimitedOptions: false,
        showXmlOptions: true,
      },
      attachTo: document.body,
    });

    const trigger = wrapper.get('button[aria-haspopup="dialog"]');
    (trigger.element as HTMLButtonElement).focus();
    await trigger.trigger("click");
    await nextTick();

    const dialog = wrapper.find('[role="dialog"][aria-label="options"]');
    expect(dialog.exists()).toBe(true);
    // Local-anchor: panel stays under the options root (BaseDropdownMenu layout).
    expect(wrapper.element.contains(dialog.element)).toBe(true);
    expect(dialog.element.parentElement).not.toBe(document.body);
    expect(dialog.classes()).toContain("absolute");
    expect(dialog.element.contains(document.activeElement)).toBe(true);
    expect(document.activeElement?.tagName).toBe("SELECT");

    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await nextTick();
    expect(wrapper.find('[role="dialog"][aria-label="options"]').exists()).toBe(false);
    expect(document.activeElement).toBe(trigger.element);

    wrapper.unmount();
  });
});
